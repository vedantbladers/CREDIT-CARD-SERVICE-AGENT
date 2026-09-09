package response

import (
	"encoding/json"
	"log"
	"net/http"
)

// JSON writes a JSON payload with the specified status code
func JSON(w http.ResponseWriter, statusCode int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("Error encoding JSON response: %v", err)
	}
}

// Error writes a standardized error JSON response
func Error(w http.ResponseWriter, statusCode int, errMsg, details string) {
	resp := map[string]string{"error": errMsg}
	if details != "" {
		resp["message"] = details
	}
	JSON(w, statusCode, resp)
}
