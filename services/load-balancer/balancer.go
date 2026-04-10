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
	IsHealthy bool
	Mutex     sync.Mutex
}

type LoadBalancer struct {
	Mutex   sync.RWMutex
	weights []float64
}

type Config struct {
	Port                string   `json:"port"`
	HealthCheckInterval string   `json:"healthCheckInterval"`
	Servers             []string `json:"servers"`
}

var servers []serverHealth

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
	scores := make([]float64, len(servers))
	for i := range servers {
		scores[i] = score(&servers[i])
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

	weights := make([]float64, len(servers))
	if sigma < 1e-9 {
		for i := range weights {
			weights[i] = 1.0 / float64(len(servers))
		}
	} else {
		var total float64
		for i, sc := range scores {
			weights[i] = 1 - normCDF(sc, mean, sigma)
			total += weights[i]
		}
		for i := range weights {
			weights[i] /= total
		}
	}

	lb.weights = weights
}

func (lb *LoadBalancer) PickServer() *serverHealth {
	lb.Mutex.RLock()
	defer lb.Mutex.RUnlock()

	r := rand.Float64()
	for i, w := range lb.weights {
		r -= w
		if r <= 0 {
			servers[i].Mutex.Lock()
			isHealthy := servers[i].IsHealthy
			servers[i].Mutex.Unlock()
			if isHealthy {
				return &servers[i]
			}
			continue
		}
	}
	// fallback: return last healthy server
	for i := len(servers) - 1; i >= 0; i-- {
		servers[i].Mutex.Lock()
		isHealthy := servers[i].IsHealthy
		servers[i].Mutex.Unlock()
		if isHealthy {
			return &servers[i]
		}
	}
	return nil
}

type checkRes struct{ cpu, mem float64 }

func checkSingleServer(ip string) (checkRes, error) {
	conn, err := grpc.NewClient(ip, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return checkRes{}, err
	}
	defer conn.Close()

	client := pb.NewHealthCheckServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	response, err := client.Check(ctx, &pb.HealthCheckRequest{})
	if err != nil {
		return checkRes{}, err
	}
	return checkRes{cpu: response.CpuUsage, mem: response.MemoryUsage}, nil
}

func healthCheck(lb *LoadBalancer, server *serverHealth, interval time.Duration) {
	for range time.Tick(interval) {
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
			log.Printf("server %s — CPU: %.1f%%, Memory: %.1f%%", server.IP, server.CPUUsage, server.MemUsage)
			if server.CPUUsage > 90.0 {
				log.Printf("WARNING: server %s CPU usage critical: %.1f%%", server.IP, server.CPUUsage)
			}
			if server.MemUsage > 90.0 {
				log.Printf("WARNING: server %s memory usage critical: %.1f%%", server.IP, server.MemUsage)
			}
		}
		server.Mutex.Unlock()

		lb.Mutex.Lock()
		lb.recomputeWeights()
		lb.Mutex.Unlock()
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

	for _, ip := range GetServerIPs(&config) {
		log.Printf("registering server: %s", ip)
		u, err := url.Parse("http://" + ip)
		if err != nil {
			log.Fatalf("invalid server address %s: %v", ip, err)
		}
		servers = append(servers, serverHealth{IP: ip, URL: u})
	}

	lb := &LoadBalancer{}
	lb.recomputeWeights()

	for i := range servers {
		go healthCheck(lb, &servers[i], healthCheckInterval)
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		server := lb.PickServer()
		if server == nil {
			http.Error(w, "no healthy server available", http.StatusServiceUnavailable)
			return
		}
		w.Header().Add("X-Forwarded-Server", server.URL.String())
		httputil.NewSingleHostReverseProxy(server.URL).ServeHTTP(w, r)
	})

	log.Println("starting load balancer on port", config.Port)
	if err = http.ListenAndServe(config.Port, nil); err != nil {
		log.Fatalf("error starting load balancer: %s", err)
	}
}
