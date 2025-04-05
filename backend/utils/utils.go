package utils

import (
	"fmt"
	"time"
)

func ValidateDate(date string) error {
	_, err := time.Parse("2006-01-02", date)
	if err != nil {
		return fmt.Errorf("must be YYYY-MM-DD format")
	}
	return nil
}
