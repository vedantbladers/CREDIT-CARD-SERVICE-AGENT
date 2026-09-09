package main

import (
	"fmt"
	"log"
	"net/http"

	"credit-card-service/go-gateway/internal/config"
	"credit-card-service/go-gateway/internal/router"
)

func main() {
	cfg := config.LoadConfig()
	r := router.NewRouter(cfg)

	addr := fmt.Sprintf("0.0.0.0:%s", cfg.Port)
	log.Printf("==================================================")
	log.Printf("🚀 Go API Gateway (Chi v5) initialized")
	log.Printf("📡 Listening on: %s", addr)
	log.Printf("🔗 Forwarding /api/chat to: %s/chat", cfg.AgentServiceURL)
	log.Printf("==================================================")

	if err := http.ListenAndServe(addr, r); err != nil {
		log.Fatalf("Fatal server failure: %v", err)
	}
}
