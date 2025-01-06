// main_test.go
package main

import (
	"testing"
)

func TestValidateDate(t *testing.T) {
	tests := []struct {
		name    string
		date    string
		wantErr bool
	}{
		{"Valid date", "2024-01-01", false},
		{"Invalid format", "01-01-2024", true},
		{"Invalid date", "2024-13-01", true},
		{"Empty date", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateDate(tt.date)
			if (err != nil) != tt.wantErr {
				t.Errorf("validateDate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
