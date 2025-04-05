package fidata

import (
	"archive/zip"
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

var getDataURL = func() string {
	return "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
}

func fetchRiskModelData() {
	// Download the zip file
	resp, err := http.Get(getDataURL())
	if err != nil {
		fmt.Printf("Error downloading data: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// Read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response: %v\n", err)
		return
	}

	// Create a reader for the zip file
	zipReader, err := zip.NewReader(bytes.NewReader(body), int64(len(body)))
	if err != nil {
		fmt.Printf("Error creating zip reader: %v\n", err)
		return
	}

	// Process the first file in the zip (which contains the data)
	file := zipReader.File[0]
	rc, err := file.Open()
	if err != nil {
		fmt.Printf("Error opening zip file: %v\n", err)
		return
	}
	defer rc.Close()

	// Create output CSV file
	outputFileName := fmt.Sprintf("fama_french_factors_%s.csv", time.Now().Format("2006-01-02"))
	outFile, err := os.Create(outputFileName)
	if err != nil {
		fmt.Printf("Error creating output file: %v\n", err)
		return
	}
	defer outFile.Close()

	// Create CSV writer
	writer := csv.NewWriter(outFile)
	defer writer.Flush()

	// Read and process the CSV data
	reader := csv.NewReader(rc)
	reader.FieldsPerRecord = -1 // Allow variable number of fields

	// Write headers
	headers := []string{"Date", "Mkt-RF", "SMB", "HML", "RF"}
	if err := writer.Write(headers); err != nil {
		fmt.Printf("Error writing headers: %v\n", err)
		return
	}

	// Skip the first few rows (metadata and headers in the original file)
	for i := 0; i < 3; i++ {
		_, err := reader.Read()
		if err != nil {
			fmt.Printf("Error skipping header rows: %v\n", err)
			return
		}
	}

	// Process each row
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Printf("Error reading record: %v\n", err)
			return
		}

		// Clean the data
		record = cleanRecord(record)
		if len(record) >= 5 {
			if err := writer.Write(record[:5]); err != nil {
				fmt.Printf("Error writing record: %v\n", err)
				return
			}
		}
	}

	fmt.Printf("Successfully downloaded and saved Fama-French data to %s\n", outputFileName)
}

func cleanRecord(record []string) []string {
	cleaned := make([]string, len(record))
	for i, field := range record {
		// Remove whitespace and handle empty fields
		cleaned[i] = strings.TrimSpace(field)
		if cleaned[i] == "" {
			cleaned[i] = "0"
		}
	}
	return cleaned
}
