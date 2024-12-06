package utils

import "strings"

func FormatNumber(s string) string {
	// Remove existing formatting
	s = strings.ReplaceAll(s, "$", "")
	s = strings.ReplaceAll(s, ",", "")

	if s == "" || s == "." {
		return "$"
	}

	// Split on decimal point if exists
	parts := strings.Split(s, ".")
	whole := parts[0]

	// Format the whole number part with commas
	if len(whole) > 3 {
		offset := len(whole) % 3
		if offset == 0 {
			offset = 3
		}
		formatted := whole[:offset]
		for i := offset; i < len(whole); i += 3 {
			formatted += "," + whole[i:i+3]
		}
		whole = formatted
	}

	// Add dollar sign
	result := "$" + whole

	// Add decimal part if exists
	if len(parts) > 1 {
		result += "." + parts[1]
	}

	return result
}

func UnformatNumber(s string) string {
	// Remove formatting for internal storage/validation
	s = strings.ReplaceAll(s, "$", "")
	s = strings.ReplaceAll(s, ",", "")
	return s
}
