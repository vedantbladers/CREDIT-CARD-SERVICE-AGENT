package handler

import (
	"net/http"
	"time"

	"credit-card-service/go-gateway/internal/response"
)

type HealthHandler struct{}

func NewHealthHandler() *HealthHandler {
	return &HealthHandler{}
}

func (h *HealthHandler) HealthCheck(w http.ResponseWriter, r *http.Request) {
	response.JSON(w, http.StatusOK, map[string]interface{}{
		"status":    "ok",
		"service":   "go-gateway",
		"router":    "chi/v5",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}
