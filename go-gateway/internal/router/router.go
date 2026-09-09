package router

import (
	"credit-card-service/go-gateway/internal/config"
	"credit-card-service/go-gateway/internal/handler"
	appMiddleware "credit-card-service/go-gateway/internal/middleware"

	"github.com/go-chi/chi/v5"
	chiMiddleware "github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func NewRouter(cfg *config.Config) *chi.Mux {
	r := chi.NewRouter()

	// Global Middlewares
	r.Use(chiMiddleware.RequestID)
	r.Use(chiMiddleware.RealIP)
	r.Use(chiMiddleware.Logger)
	r.Use(chiMiddleware.Recoverer)

	// Cross-Origin Resource Sharing (CORS)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300,
	}))

	// Handlers
	healthHandler := handler.NewHealthHandler()
	tokenHandler := handler.NewTokenHandler(cfg)
	chatHandler := handler.NewChatHandler(cfg)

	// Public Routes
	r.Get("/health", healthHandler.HealthCheck)
	r.Get("/api/token/test", tokenHandler.IssueTestToken)
	r.Post("/api/token/test", tokenHandler.IssueTestToken)

	// Protected Routes (Protected by JWT)
	r.Group(func(protected chi.Router) {
		protected.Use(appMiddleware.JWTAuthMiddleware(cfg.JWTSecret))
		protected.Post("/api/chat", chatHandler.ForwardChat)
	})

	return r
}
