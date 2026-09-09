package config

import (
	"os"
)

type Config struct {
	Port            string
	JWTSecret       []byte
	AgentServiceURL string
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

func LoadConfig() *Config {
	return &Config{
		Port:            getEnv("PORT", "8080"),
		JWTSecret:       []byte(getEnv("JWT_SECRET", "academic-project-secret-key-2026")),
		AgentServiceURL: getEnv("AGENT_SERVICE_URL", "http://fastapi-agent:8000"),
	}
}
