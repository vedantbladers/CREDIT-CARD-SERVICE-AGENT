package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"credit-card-service/go-gateway/internal/config"
	"credit-card-service/go-gateway/internal/middleware"
	"credit-card-service/go-gateway/internal/response"
)

type ChatHandler struct {
	cfg        *config.Config
	httpClient *http.Client
}

func NewChatHandler(cfg *config.Config) *ChatHandler {
	return &ChatHandler{
		cfg: cfg,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// ForwardChat proxies chat requests to the downstream FastAPI orchestrator
func (h *ChatHandler) ForwardChat(w http.ResponseWriter, r *http.Request) {
	// 1. Retrieve validated claims from context
	claims, ok := middleware.GetClaims(r.Context())
	if !ok {
		response.Error(w, http.StatusUnauthorized, "Unauthorized", "User context not found in request")
		return
	}

	// 2. Parse incoming payload
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		response.Error(w, http.StatusBadRequest, "BadRequest", "Failed to read request body")
		return
	}
	defer r.Body.Close()

	var payload map[string]interface{}
	if err := json.Unmarshal(bodyBytes, &payload); err != nil {
		response.Error(w, http.StatusBadRequest, "BadRequest", "Invalid JSON body")
		return
	}

	// 3. Inject authenticated account_id from JWT subject if omitted
	if _, exists := payload["account_id"]; !exists {
		if sub, ok := claims["sub"].(string); ok {
			payload["account_id"] = sub
		}
	}

	forwardBytes, err := json.Marshal(payload)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to serialize payload")
		return
	}

	// 4. Forward to FastAPI Agent Orchestrator
	targetURL := fmt.Sprintf("%s/chat", h.cfg.AgentServiceURL)
	req, err := http.NewRequestWithContext(r.Context(), http.MethodPost, targetURL, bytes.NewBuffer(forwardBytes))
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to create upstream request")
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		log.Printf("[Gateway Error] Upstream call to %s failed: %v", targetURL, err)
		response.Error(w, http.StatusBadGateway, "BadGateway", fmt.Sprintf("Failed to reach FastAPI agent: %v", err))
		return
	}
	defer resp.Body.Close()

	// 5. Return upstream response
	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to read upstream response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(resp.StatusCode)
	w.Write(respBytes)
}
