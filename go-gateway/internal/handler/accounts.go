package handler

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"credit-card-service/go-gateway/internal/config"
	"credit-card-service/go-gateway/internal/response"
)

type AccountsHandler struct {
	cfg        *config.Config
	httpClient *http.Client
}

func NewAccountsHandler(cfg *config.Config) *AccountsHandler {
	return &AccountsHandler{
		cfg: cfg,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// ForwardAccounts proxies accounts query to the downstream FastAPI orchestrator
func (h *AccountsHandler) ForwardAccounts(w http.ResponseWriter, r *http.Request) {
	targetURL := fmt.Sprintf("%s/accounts", h.cfg.AgentServiceURL)
	req, err := http.NewRequestWithContext(r.Context(), http.MethodGet, targetURL, nil)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to create upstream request")
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		log.Printf("[Gateway Error] Upstream call to %s failed: %v", targetURL, err)
		response.Error(w, http.StatusBadGateway, "BadGateway", fmt.Sprintf("Failed to reach FastAPI agent: %v", err))
		return
	}
	defer resp.Body.Close()

	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to read upstream response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(resp.StatusCode)
	w.Write(respBytes)
}
