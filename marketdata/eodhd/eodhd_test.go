package eodhd

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

type MockHTTPClient struct {
	Responses map[string]*http.Response
}

func (m *MockHTTPClient) RoundTrip(req *http.Request) (*http.Response, error) {
	if resp, ok := m.Responses[req.URL.String()]; ok {
		return resp, nil
	}
	return nil, fmt.Errorf("no response found for %s", req.URL.String())
}

func TestClient_GetPrices(t *testing.T) {
	mockClient := &MockHTTPClient{
		Responses: make(map[string]*http.Response),
	}
	httpClient := &http.Client{
		Transport: mockClient,
	}
	client := &Client{
		apiKey:     "test_api_key",
		httpClient: httpClient,
	}

	startDate := "2023-10-26"
	endDate := "2023-10-27"

	t.Run("Success", func(t *testing.T) {
		symbols := []string{"AAPL", "MSFT"}
		expectedURL1 := fmt.Sprintf("https://eodhd.com/api/eod/AAPL?from=%s&to=%s&api_token=%s&fmt=json", startDate, endDate, client.apiKey)
		expectedURL2 := fmt.Sprintf("https://eodhd.com/api/eod/MSFT?from=%s&to=%s&api_token=%s&fmt=json", startDate, endDate, client.apiKey)

		// Define JSON responses as strings
		jsonResponse1 := `[{"date":"2023-10-26","open":100,"high":101,"low":99,"close":100.5,"adjusted_close":100.5,"volume":1000}]`
		jsonResponse2 := `[{"date":"2023-10-26","open":200,"high":201,"low":199,"close":200.5,"adjusted_close":200.5,"volume":2000}]`

		// Create http.Response objects
		mockClient.Responses[expectedURL1] = &http.Response{
			StatusCode: http.StatusOK,
			Body:       io.NopCloser(bytes.NewReader([]byte(jsonResponse1))),
		}
		mockClient.Responses[expectedURL2] = &http.Response{
			StatusCode: http.StatusOK,
			Body:       io.NopCloser(bytes.NewReader([]byte(jsonResponse2))),
		}

		prices, err := client.GetPrices(symbols, startDate, endDate)
		if err != nil {
			t.Errorf("GetPrices() error = %v", err)
			return
		}

		expectedPrices := map[string][]StockPrice{
			"AAPL": {{"2023-10-26", 100, 101, 99, 100.5, 100.5, 1000}},
			"MSFT": {{"2023-10-26", 200, 201, 199, 200.5, 200.5, 2000}},
		}

		if diff := cmp.Diff(expectedPrices, prices); diff != "" {
			t.Errorf("GetPrices() mismatch (-want +got):\n%s", diff)
		}

	})
}
