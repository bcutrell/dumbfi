package main

import (
	"fmt"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"log"
	"strconv"
	"strings"

	utils "dumbfi/utils"
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

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "$10,000"
	ti.Focus()
	ti.CharLimit = 20
	ti.Width = 20

	// Set validation for numbers and decimal point only
	ti.Validate = func(s string) error {
		raw := utils.UnformatNumber(s)
		if raw == "" || raw == "." {
			return nil
		}
		// Allow only one decimal point
		if strings.Count(raw, ".") > 1 {
			return fmt.Errorf("only one decimal point allowed")
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
			rawValue := utils.UnformatNumber(m.textInput.Value())
			if rawValue != "" {
				// number TODO pass raw number to backtest
				if val, err := strconv.ParseFloat(rawValue, 64); err == nil {
					fmt.Printf("\nInitial Cash: %.2f\n", val)
				}
			}
			return m, tea.Quit
		case tea.KeyCtrlC, tea.KeyEsc:
			return m, tea.Quit
		case tea.KeyBackspace:
			// Prevent backspace from removing the dollar sign
			if len(m.textInput.Value()) <= 1 {
				return m, nil
			}

			// Handle backspace normally for other cases
			m.textInput, cmd = m.textInput.Update(msg)

			// Ensure dollar sign is maintained
			if !strings.HasPrefix(m.textInput.Value(), "$") {
				m.textInput.SetValue("$" + m.textInput.Value())
			}

			return m, cmd
		}
	case errMsg:
		m.err = msg
		return m, nil
	}

	m.textInput, cmd = m.textInput.Update(msg)

	// Maintain formatting after each update
	if val := m.textInput.Value(); val != "" {
		// Store cursor position before formatting
		cursorPos := m.textInput.Position()

		// Ensure dollar sign is always present
		if !strings.HasPrefix(val, "$") {
			val = "$" + val
			cursorPos++ // Adjust cursor for added dollar sign
		}

		// Format the number
		formatted := utils.FormatNumber(val)

		// Calculate the difference in length after formatting
		lenDiff := len(formatted) - len(val)

		// Set the formatted value
		m.textInput.SetValue(formatted)

		// Adjust cursor position based on formatting changes
		newCursorPos := cursorPos + lenDiff
		if newCursorPos < 1 {
			newCursorPos = 1
		}
		if newCursorPos > len(formatted) {
			newCursorPos = len(formatted)
		}
		m.textInput.SetCursor(newCursorPos)
	}

	return m, cmd
}

func (m model) View() string {
	var sb strings.Builder

	sb.WriteString("Enter initial cash balance:\n\n")
	sb.WriteString(m.textInput.View())
	sb.WriteString("\n\n")

	// Display validation errors if any
	if m.err != nil {
		sb.WriteString("Error")
	}

	sb.WriteString("(esc to quit)\n")

	return sb.String()
}
