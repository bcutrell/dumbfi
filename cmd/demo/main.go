// main.go
package main

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Styles
var (
	primaryStyle = lipgloss.NewStyle().
			BorderStyle(lipgloss.NormalBorder()).
			BorderForeground(lipgloss.Color("62")).
			Padding(1)

	headerStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("62"))

	inputStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("205"))

	errorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("196"))
)

// Asset represents a portfolio asset
type Asset struct {
	ticker     string
	allocation float64
}

// Model represents the application state
type Model struct {
	assets        []Asset
	cursor        int
	startDate     string
	endDate       string
	initialAmount float64
	rebalancing   string
	inputMode     bool
	activeInput   string
	err           error
	width         int
	height        int
	results       *BacktestResults
}

type BacktestResults struct {
	cagr        float64
	stdev       float64
	sharpe      float64
	maxDrawdown float64
}

func initialModel() Model {
	return Model{
		assets: []Asset{
			{ticker: "VTI", allocation: 60.0},
			{ticker: "BND", allocation: 40.0},
		},
		startDate:     "2010-01",
		endDate:       "2023-12",
		initialAmount: 10000,
		rebalancing:   "Monthly",
		cursor:        0,
	}
}

func (m Model) Init() tea.Cmd {
	return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "up", "k":
			if m.cursor > 0 {
				m.cursor--
			}
		case "down", "j":
			if m.cursor < len(m.assets)+4 { // +4 for date, amount, rebalancing
				m.cursor++
			}
		case "enter":
			if !m.inputMode {
				m.inputMode = true
				m.activeInput = m.getCurrentField()
			} else {
				m.inputMode = false
				m.activeInput = ""
			}
		case "r":
			if !m.inputMode {
				m.results = runBacktest(m) // Implement actual backtesting logic
			}
		}
	}

	return m, nil
}

func (m Model) getCurrentField() string {
	if m.cursor < len(m.assets) {
		return fmt.Sprintf("asset_%d", m.cursor)
	}
	switch m.cursor - len(m.assets) {
	case 0:
		return "start_date"
	case 1:
		return "end_date"
	case 2:
		return "initial_amount"
	case 3:
		return "rebalancing"
	}
	return ""
}

func (m Model) View() string {
	var b strings.Builder

	// Header
	b.WriteString(headerStyle.Render("Portfolio Backtest TUI\n\n"))

	// Configuration section
	config := strings.Builder{}
	config.WriteString("Time Period and Settings\n")
	config.WriteString(fmt.Sprintf("Start Date: %s\n", highlightIfSelected(m, "start_date", m.startDate)))
	config.WriteString(fmt.Sprintf("End Date: %s\n", highlightIfSelected(m, "end_date", m.endDate)))
	config.WriteString(fmt.Sprintf("Initial Amount: $%.2f\n", m.initialAmount))
	config.WriteString(fmt.Sprintf("Rebalancing: %s\n\n", m.rebalancing))

	// Portfolio allocation
	config.WriteString("Portfolio Allocation\n")
	config.WriteString("Asset    Allocation\n")
	for i, asset := range m.assets {
		cursor := " "
		if m.cursor == i && !m.inputMode {
			cursor = ">"
		}
		config.WriteString(fmt.Sprintf("%s %-7s  %.1f%%\n", cursor, asset.ticker, asset.allocation))
	}

	b.WriteString(primaryStyle.Render(config.String()))

	// Results section
	if m.results != nil {
		results := strings.Builder{}
		results.WriteString("Backtest Results\n")
		results.WriteString(fmt.Sprintf("CAGR: %.2f%%\n", m.results.cagr))
		results.WriteString(fmt.Sprintf("Std Dev: %.2f%%\n", m.results.stdev))
		results.WriteString(fmt.Sprintf("Sharpe Ratio: %.2f\n", m.results.sharpe))
		results.WriteString(fmt.Sprintf("Max Drawdown: %.2f%%\n", m.results.maxDrawdown))
		b.WriteString(primaryStyle.Render(results.String()))
	}

	// Help
	help := "\nq: quit • ↑/↓: navigate • enter: edit • r: run backtest"
	b.WriteString(help)

	return b.String()
}

func highlightIfSelected(m Model, field, value string) string {
	if m.inputMode && m.activeInput == field {
		return inputStyle.Render(value + "▋")
	}
	return value
}

func runBacktest(m Model) *BacktestResults {
	// Simplified mock results - replace with actual backtesting logic
	return &BacktestResults{
		cagr:        8.5,
		stdev:       12.3,
		sharpe:      0.69,
		maxDrawdown: -15.4,
	}
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running program: %v", err)
	}
}
