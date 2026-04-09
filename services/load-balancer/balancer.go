package main

import (
	"context"
	"log"
	"math"
	"math/rand"
	"os"
	"strings"
	"sync"
	"sync/atomic" // Required for atomic snapshot
	"time"

	pb "load-balancer/generated/health-check"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type serverHealth struct {
	IP        string
	CPUUsage  float32
	MemUsage  float32
	LastCheck time.Time
}

var (
	servers []serverHealth
	mu      sync.RWMutex
	// snap stores the latest []serverHealth snapshot atomically
	snap atomic.Value
)

func GetServerIPs() []string {
	ips := os.Getenv("SERVER_IPS")
	return strings.Split(ips, ",")
}

// --- weight math (unchanged) ---
// erf, normCDF, and score functions remain the same...
// [Truncated for brevity]

// PickServer attempts to update the global snapshot.
// If the mutex is locked, it immediately uses the last known snapshot.
func PickServer() *serverHealth {
	// 1. Try to get a lock to refresh the snapshot
	if mu.TryRLock() {
		newSnap := make([]serverHealth, len(servers))
		copy(newSnap, servers)
		snap.Store(newSnap) // Atomically update the global snap
		mu.RUnlock()
	}

	// 2. Load the current snapshot (will be the "old" one if TryRLock failed)
	s, ok := snap.Load().([]serverHealth)
	if !ok || len(s) == 0 {
		return nil
	}

	scores := make([]float64, len(s))
	for i, server := range s {
		scores[i] = score(server)
	}

	// ... [Rest of your Inverse-CDF logic using 's' instead of 'snap'] ...
	// Note: ensure you use the local variable 's' for the math below

	var sum, mean float64
	for _, sc := range scores {
		sum += sc
	}
	mean = sum / float64(len(scores))

	var variance float64
	for _, sc := range scores {
		diff := sc - mean
		variance += diff * diff
	}
	sigma := math.Sqrt(variance / float64(len(scores)))

	weights := make([]float64, len(s))
	if sigma < 1e-9 {
		for i := range weights {
			weights[i] = 1.0 / float64(len(s))
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

	r := rand.Float64()
	for i, w := range weights {
		r -= w
		if r <= 0 {
			return &s[i]
		}
	}
	return &s[len(s)-1]
}

// healthCheck now updates the master 'servers' slice
func healthCheck() {
	for {
		// Optimization: Don't hold the lock for the ENTIRE duration of network calls.
		// That would block PickServer for seconds.
		for i := range servers {
			// Perform gRPC call outside of the lock
			res, err := checkSingleServer(servers[i].IP)
			if err != nil {
				log.Printf("error checking %s: %v", servers[i].IP, err)
				continue
			}

			// Only lock when writing the data back to the master slice
			mu.Lock()
			servers[i].CPUUsage = res.cpu
			servers[i].MemUsage = res.mem
			servers[i].LastCheck = time.Now()
			mu.Unlock()
		}
		time.Sleep(10 * time.Second)
	}
}

type checkRes struct{ cpu, mem float32 }

func checkSingleServer(ip string) (checkRes, error) {
	conn, err := grpc.NewClient(ip, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return checkRes{}, err
	}
	defer conn.Close()

	client := pb.NewHealthCheckClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	response, err := client.Check(ctx, &pb.HealthCheckRequest{})
	if err != nil {
		return checkRes{}, err
	}
	return checkRes{cpu: response.GetCpuUsage(), mem: response.GetMemoryUsage()}, nil
}

func main() {
	initialServers := []serverHealth{}
	for _, ip := range GetServerIPs() {
		log.Printf("registering server: %s", ip)
		initialServers = append(initialServers, serverHealth{IP: ip})
	}
	servers = initialServers

	// Initialize the atomic snapshot so PickServer doesn't crash on start
	snap.Store(servers)

	go healthCheck()
	select {}
}
