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
	// CLI
	port := flag.Int("port", 8080, "Port to serve on")
	directory := flag.String("dir", "./public", "Directory to serve static files from")
	flag.Parse()

	if _, err := os.Stat(*directory); os.IsNotExist(err) {
		log.Fatalf("Directory %s does not exist", *directory)
	}

	fileServer := http.FileServer(http.Dir(*directory))

	// Routes
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("%s %s", r.Method, r.URL.Path)
		fileServer.ServeHTTP(w, r)
		log.Printf("Completed in %v", time.Since(start))
	})
	http.Handle("/", handler)

	// 404
	http.HandleFunc("/404", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
		fmt.Fprint(w, "404 Page Not Found")
	})

	// Server
	serverAddr := fmt.Sprintf(":%d", *port)
	log.Printf("Server started at http://localhost%s", serverAddr)
	log.Printf("Serving files from %s", *directory)

	err := http.ListenAndServe(serverAddr, nil)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
