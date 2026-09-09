package middleware

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"credit-card-service/go-gateway/internal/response"

	"github.com/golang-jwt/jwt/v5"
)

type contextKey string

const ClaimsKey contextKey = "jwt_claims"

// JWTAuthMiddleware validates Bearer JWT tokens against the secret
func JWTAuthMiddleware(jwtSecret []byte) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				response.Error(w, http.StatusUnauthorized, "Unauthorized", "missing Authorization header")
				return
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
				response.Error(w, http.StatusUnauthorized, "Unauthorized", "invalid Authorization header format, expected 'Bearer <token>'")
				return
			}

			tokenString := parts[1]
			claims := jwt.MapClaims{}

			token, err := jwt.ParseWithClaims(tokenString, claims, func(t *jwt.Token) (interface{}, error) {
				if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
					return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
				}
				return jwtSecret, nil
			})

			if err != nil || !token.Valid {
				response.Error(w, http.StatusUnauthorized, "Unauthorized", fmt.Sprintf("invalid or expired token: %v", err))
				return
			}

			// Store claims in request context for downstream handlers
			ctx := context.WithValue(r.Context(), ClaimsKey, claims)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// GetClaims retrieves validated JWT claims from request context
func GetClaims(ctx context.Context) (jwt.MapClaims, bool) {
	claims, ok := ctx.Value(ClaimsKey).(jwt.MapClaims)
	return claims, ok
}
