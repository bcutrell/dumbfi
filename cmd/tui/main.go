package main

import (
	"fmt"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"log"
	"strconv"
	"strings"
)

const logo = `
 ____                    _     _____ _ 
|  _ \  _   _ _ __ ___ | |__ |  ___(_)
| | | || | | | '_ ' _ \| '_ \| |_  | |
| |_| || |_| | | | | | | |_) |  _| | |
|____/ \__,_|_| |_| |_|_.__/|_|   |_|
`

var (
	logoStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#01FAC6")).Bold(true)
)

func main() {
	fmt.Printf("%s\n", logoStyle.Render(logo))
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		log.Fatal(err)
	}
}

type (
	errMsg error
)

type model struct {
	textInput textinput.Model
	err       error
}

func formatNumber(s string) string {
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

func unformatNumber(s string) string {
	// Remove formatting for internal storage/validation
	s = strings.ReplaceAll(s, "$", "")
	s = strings.ReplaceAll(s, ",", "")
	return s
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "$10,000"
	ti.Focus()
	ti.CharLimit = 20
	ti.Width = 20

	// Set validation for numbers and decimal point only
	ti.Validate = func(s string) error {
		raw := unformatNumber(s)
		if raw == "" || raw == "." {
			return nil
		}
		// Allow only one decimal point
		if strings.Count(raw, ".") > 1 {
			return fmt.Errorf("invalid number format")
		}
		// Check if all other characters are digits
		for _, r := range strings.ReplaceAll(raw, ".", "") {
			if r < '0' || r > '9' {
				return fmt.Errorf("please enter numbers only")
			}
		}
		return nil
	}

	// Add custom value formatter
	ti.SetValue("$")

	return model{
		textInput: ti,
		err:       nil,
	}
}

func (m model) Init() tea.Cmd {
	return textinput.Blink
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyEnter:
			// Get the raw number value
			rawValue := unformatNumber(m.textInput.Value())
			if rawValue != "" {
				// number TODO pass raw number to backtest
				if val, err := strconv.ParseFloat(rawValue, 64); err == nil {
					fmt.Printf("\nInitial Cash: %.2f\n", val)
				}
			}
			return m, tea.Quit
		case tea.KeyCtrlC, tea.KeyEsc:
			return m, tea.Quit
		default:
			// Handle backspace specially to maintain the dollar sign
			if msg.Type == tea.KeyBackspace && m.textInput.Value() == "$" {
				return m, cmd
			}
		}
	case errMsg:
		m.err = msg
		return m, nil
	}

	m.textInput, cmd = m.textInput.Update(msg)

	// Format the number after each update
	if m.textInput.Value() != "" {
		m.textInput.SetValue(formatNumber(m.textInput.Value()))
	}

	return m, cmd
}

func (m model) View() string {
	return fmt.Sprintf(
		"Enter initial cash balance:\n\n%s\n\n%s",
		m.textInput.View(),
		"(esc to quit)",
	) + "\n"
}
