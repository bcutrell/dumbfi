package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	// Command line flags
	port := flag.Int("port", 8080, "Port to serve on")
	directory := flag.String("dir", "./public", "Directory to serve static files from")
	flag.Parse()

	// Ensure the directory exists
	if _, err := os.Stat(*directory); os.IsNotExist(err) {
		log.Fatalf("Directory %s does not exist", *directory)
	}

	fileServer := http.FileServer(http.Dir(*directory))
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("%s %s", r.Method, r.URL.Path)
		fileServer.ServeHTTP(w, r)
		log.Printf("Completed in %v", time.Since(start))
	})

	// Setup routes
	http.Handle("/", handler)

	// Handle 404s by checking if the file exists first
	http.HandleFunc("/404", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
		fmt.Fprint(w, "404 Page Not Found")
	})

	// Setup single page application (SPA) support - all unmatched routes serve index.html
	// Uncomment this if you need SPA support
	/*
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			// Check if the file exists in the filesystem
			path := filepath.Join(*directory, r.URL.Path)
			_, err := os.Stat(path)

			// If file doesn't exist, serve index.html for SPA routing
			if os.IsNotExist(err) {
				http.ServeFile(w, r, filepath.Join(*directory, "index.html"))
				return
			}

			// Otherwise, serve the file
			fileServer.ServeHTTP(w, r)
		})
	*/

	// Start the server
	serverAddr := fmt.Sprintf(":%d", *port)
	log.Printf("Server started at http://localhost%s", serverAddr)
	log.Printf("Serving files from %s", *directory)

	err := http.ListenAndServe(serverAddr, nil)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
