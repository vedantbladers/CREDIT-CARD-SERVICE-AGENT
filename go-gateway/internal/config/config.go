package config

import (
	"os"
	"strings"
)

type Config struct {
	Port             string
	JWTSecret        []byte
	AgentServiceURL  string
	EnableTestTokens bool
	AllowedOrigins   []string
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

func LoadConfig() *Config {
	allowTest := os.Getenv("ENABLE_TEST_TOKENS") != "false"
	originsStr := getEnv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
	var origins []string
	for _, o := range strings.Split(originsStr, ",") {
		trimmed := strings.TrimSpace(o)
		if trimmed != "" {
			origins = append(origins, trimmed)
		}
	}
	if len(origins) == 0 {
		origins = []string{"http://localhost:5173", "http://127.0.0.1:5173"}
	}

	return &Config{
		Port:             getEnv("PORT", "8080"),
		JWTSecret:        []byte(getEnv("JWT_SECRET", "academic-project-secret-key-2026")),
		AgentServiceURL:  getEnv("AGENT_SERVICE_URL", "http://fastapi-agent:8000"),
		EnableTestTokens: allowTest,
		AllowedOrigins:   origins,
	}
}
