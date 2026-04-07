package main

import (
	"context"
	"log"
	"os"
	"strings"
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



func GetServerIPs() []string {
	ips := os.Getenv("SERVER_IPS")
	return strings.Split(ips, ",")
}
func healthCheck() {
	for {
		for _, server := range servers {
			conn, err := grpc.NewClient(server.IP, grpc.WithTransportCredentials(insecure.NewCredentials()))
			if err != nil {
				log.Printf("failed to connect to %s: %v", server.IP, err)
				continue
			}

			client := pb.NewHealthCheckClient(conn)

			ctx, cancel := context.WithTimeout(context.Background(), time.Second)
			response, err := client.Check(ctx, &pb.HealthCheckRequest{})
			cancel()
			conn.Close()

			if err != nil {
				log.Printf("error checking health of server %s: %v", ip, err)
				continue
			}
			server.CPUUsage = response.GetCpuUsage()
			server.MemUsage = response.GetMemoryUsage()
			server.LastCheck = time.Now()

			log.Printf("server %s — CPU: %.1f%%, Memory: %.1f%%",
				server.IP,
				server.CPUUsage,
				server.MemUsage,
			)

			// Example threshold-based alerting
			if server.CPUUsage > 90.0 {
				log.Printf("WARNING: server %s CPU usage critical: %.1f%%", server.IP, server.CPUUsage)
			}
			if server.MemUsage > 90.0 {
				log.Printf("WARNING: server %s memory usage critical: %.1f%%", server.IP, server.MemUsage)
			}
		}

		time.Sleep(10 * time.Second)
	}
}

servers := []serverHealth{}
func main() {
	serverIPs := GetServerIPs()
	for _, ip := range serverIPs {
		log.Printf("API Gateway Server IP: %s", ip)
		servers = append(servers, serverHealth{IP: ip})
	}

	go healthCheck()

	// Block forever — keep main alive so the goroutine can run
	select {}
}
