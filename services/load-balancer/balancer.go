package main

import (
	"context"
	"encoding/json"
	"log"
	"math"
	"math/rand"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"sync"
	"time"

	pb "github.com/hamadalghanim/distred/generated"

	"gonum.org/v1/gonum/stat/distuv"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type serverHealth struct {
	IP        string
	CPUUsage  float64
	MemUsage  float64
	LastCheck time.Time
	URL       *url.URL
	Proxy     *httputil.ReverseProxy
	IsHealthy bool
	Mutex     sync.RWMutex
}

type LoadBalancer struct {
	sync.RWMutex
	weights []float64
	servers []*serverHealth
}
type Config struct {
	Port                string   `json:"port"`
	HealthCheckInterval string   `json:"healthCheckInterval"`
	Servers             []string `json:"servers"`
}

func loadConfig(file string) (Config, error) {
	var config Config
	data, err := os.ReadFile(file)
	if err != nil {
		return config, err
	}
	err = json.Unmarshal(data, &config)
	return config, err
}

func GetServerIPs(config *Config) []string {
	ips := os.Getenv("SERVER_IPS")

	if ips == "" {
		return config.Servers
	}
	return strings.Split(ips, ",")
}

func normCDF(x, mu, sigma float64) float64 {
	normal := distuv.Normal{Mu: mu, Sigma: sigma}
	return normal.CDF(x)
}

func score(s *serverHealth) float64 {
	return 0.95*float64(s.CPUUsage) + 0.05*float64(s.MemUsage)
}

func (lb *LoadBalancer) recomputeWeights() {
	lb.Lock()
	defer lb.Unlock()

	scores := make([]float64, len(lb.servers))
	for i, s := range lb.servers {
		s.Mutex.RLock()
		scores[i] = score(s)
		s.Mutex.RUnlock()
	}

	var sum float64
	for _, sc := range scores {
		sum += sc
	}
	mean := sum / float64(len(scores))

	var variance float64
	for _, sc := range scores {
		diff := sc - mean
		variance += diff * diff
	}
	sigma := math.Sqrt(variance / float64(len(scores)))

	weights := make([]float64, len(lb.servers))
	if sigma < 1e-9 {
		for i := range weights {
			weights[i] = 1.0 / float64(len(lb.servers))
		}
	} else {
		var total float64
		for i, sc := range scores {
			weights[i] = 1 - normCDF(sc, mean, sigma)
			total += weights[i]
		}
		if total > 0 {
			for i := range weights {
				weights[i] /= total
			}
		} else {
			for i := range weights {
				weights[i] = 1.0 / float64(len(lb.servers))
			}
		}
	}

	lb.weights = weights
}

func (lb *LoadBalancer) PickServer() *serverHealth {
	lb.RLock()
	weights := lb.weights
	lb.RUnlock()

	r := rand.Float64()
	for i, w := range weights {
		r -= w
		if r <= 0 {
			s := lb.servers[i]
			s.Mutex.RLock()
			isHealthy := s.IsHealthy
			s.Mutex.RUnlock()
			if isHealthy {
				return s
			}
			break // try fallback if picked is unhealthy
		}
	}

	// fallback: find first healthy server
	for _, s := range lb.servers {
		s.Mutex.RLock()
		isHealthy := s.IsHealthy
		s.Mutex.RUnlock()
		if isHealthy {
			return s
		}
	}
	return nil
}

type checkRes struct{ cpu, mem float64 }

func checkSingleServer(ip string) (checkRes, error) {
	conn, err := grpc.NewClient(ip+":50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return checkRes{}, err
	}
	defer conn.Close()

	client := pb.NewHealthCheckServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	response, err := client.Check(ctx, &pb.HealthCheckRequest{})
	if err != nil {
		return checkRes{}, err
	}
	return checkRes{cpu: response.CpuUsage, mem: response.MemoryUsage}, nil
}

func healthCheck(lb *LoadBalancer, server *serverHealth, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	for range ticker.C {
		res, err := checkSingleServer(server.IP)

		server.Mutex.Lock()
		if err != nil {
			log.Printf("error checking %s: %v", server.IP, err)
			server.IsHealthy = false
		} else {
			server.CPUUsage = res.cpu
			server.MemUsage = res.mem
			server.LastCheck = time.Now()
			server.IsHealthy = true
			if server.CPUUsage > 90.0 {
				log.Printf("WARNING: server %s CPU usage critical: %.1f%%", server.IP, server.CPUUsage)
			}
			if server.MemUsage > 90.0 {
				log.Printf("WARNING: server %s memory usage critical: %.1f%%", server.IP, server.MemUsage)
			}
		}
		server.Mutex.Unlock()
	}
}

func main() {
	config, err := loadConfig("config.json")
	if err != nil {
		log.Fatalf("error loading configuration: %s", err)
	}

	healthCheckInterval, err := time.ParseDuration(config.HealthCheckInterval)
	if err != nil {
		log.Fatalf("invalid health check interval: %s", err)
	}

	lb := &LoadBalancer{}

	for _, ip := range GetServerIPs(&config) {
		log.Printf("registering server: %s", ip)
		u, err := url.Parse("http://" + ip + config.Port)
		if err != nil {
			log.Fatalf("invalid server address %s: %v", ip, err)
		}
		proxy := httputil.NewSingleHostReverseProxy(u)
		// Tune proxy for performance
		proxy.Transport = &http.Transport{
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 100,
			IdleConnTimeout:     90 * time.Second,
		}

		s := &serverHealth{IP: ip, URL: u, Proxy: proxy, IsHealthy: true}
		lb.servers = append(lb.servers, s)
	}

	lb.recomputeWeights()

	for _, s := range lb.servers {
		go healthCheck(lb, s, healthCheckInterval)
	}

	// Periodic weight recomputation to avoid doing it in every health check loop
	go func() {
		ticker := time.NewTicker(2 * time.Second)
		for range ticker.C {
			lb.recomputeWeights()
		}
	}()

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		server := lb.PickServer()
		if server == nil {
			http.Error(w, "no healthy server available", http.StatusServiceUnavailable)
			return
		}
		server.Proxy.ServeHTTP(w, r)
	})

	log.Println("starting load balancer on port", config.Port)
	server := &http.Server{
		Addr:         config.Port,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	if err = server.ListenAndServe(); err != nil {
		log.Fatalf("error starting load balancer: %s", err)
	}
}
