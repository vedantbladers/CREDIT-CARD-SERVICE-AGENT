package handler

import (
	"net/http"
	"time"

	"credit-card-service/go-gateway/internal/config"
	"credit-card-service/go-gateway/internal/response"

	"github.com/golang-jwt/jwt/v5"
)

type TokenHandler struct {
	cfg *config.Config
}

func NewTokenHandler(cfg *config.Config) *TokenHandler {
	return &TokenHandler{cfg: cfg}
}

// IssueTestToken generates a signed mock JWT for local development and verification
func (h *TokenHandler) IssueTestToken(w http.ResponseWriter, r *http.Request) {
	accountID := r.URL.Query().Get("account_id")
	if accountID == "" {
		accountID = "ACC-1001"
	}

	nameMap := map[string]string{
		"ACC-1001": "Alice Johnson",
		"ACC-1002": "Bob Smith",
		"ACC-1003": "Charlie Brown",
		"ACC-1004": "Dana Scully",
	}
	userName := nameMap[accountID]
	if userName == "" {
		userName = "Cardholder " + accountID
	}

	claims := jwt.MapClaims{
		"sub":   accountID,
		"name":  userName,
		"role":  "cardholder",
		"exp":   time.Now().Add(24 * time.Hour).Unix(),
		"iat":   time.Now().Unix(),
		"iss":   "credit-card-gateway",
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(h.cfg.JWTSecret)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "InternalServerError", "Failed to generate test token")
		return
	}

	response.JSON(w, http.StatusOK, map[string]interface{}{
		"token":      tokenString,
		"token_type": "Bearer",
		"account_id": accountID,
		"name":       userName,
		"expires_in": 86400,
		"note":       "Mock test token issued by Go Gateway (Chi) for verification",
	})
}
