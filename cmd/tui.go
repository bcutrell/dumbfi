package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"dumbfi/internal/database"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	_ "modernc.org/sqlite"
)

// Styles
var (
	docStyle = lipgloss.NewStyle().Margin(1, 2)

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FAFAFA")).
			Background(lipgloss.Color("#7D56F4")).
			Padding(0, 1)

	errorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF0000"))
)

type model struct {
	table         table.Model
	textInput     textinput.Model
	portfolioData []database.PortfolioData
	err           error
	message       string
	isAdding      bool
}

func initialModel() model {
	columns := []table.Column{
		{Title: "Date", Width: 20},
		{Title: "Cash", Width: 15},
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithFocused(true),
		table.WithHeight(10),
	)

	// Set table styles
	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240")).
		BorderBottom(true).
		Bold(false)
	s.Selected = s.Selected.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(false)
	t.SetStyles(s)

	// Initialize text input
	ti := textinput.New()
	ti.Placeholder = "Enter cash amount..."
	ti.CharLimit = 15
	ti.Width = 20

	return model{
		table:     t,
		textInput: ti,
		isAdding:  false,
	}
}

func (m model) Init() tea.Cmd {
	return fetchDataCmd
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "a":
			if !m.isAdding {
				m.isAdding = true
				m.textInput.Focus()
				return m, textinput.Blink
			}
		case "esc":
			if m.isAdding {
				m.isAdding = false
				m.textInput.Blur()
				return m, nil
			}
		case "enter":
			if m.isAdding {
				return m.handleAddEntry()
			}
		}

	case fetchDataMsg:
		m.portfolioData = msg
		m.updateTableRows()
		return m, nil

	case errMsg:
		m.err = msg
		return m, nil
	}

	if m.isAdding {
		m.textInput, cmd = m.textInput.Update(msg)
		return m, cmd
	}

	return m, cmd
}

func (m model) View() string {
	var s strings.Builder

	// Title
	s.WriteString(titleStyle.Render("Portfolio Dashboard") + "\n\n")

	// Table
	s.WriteString(m.table.View() + "\n\n")

	// Input or help text
	if m.isAdding {
		s.WriteString("Enter amount: " + m.textInput.View() + "\n")
		s.WriteString("Press Enter to submit, ESC to cancel\n")
	} else {
		s.WriteString("Press 'a' to add entry, 'q' to quit\n")
	}

	// Message (success/error)
	if m.message != "" {
		s.WriteString("\n" + m.message + "\n")
	}
	if m.err != nil {
		s.WriteString("\n" + errorStyle.Render(m.err.Error()) + "\n")
	}

	return docStyle.Render(s.String())
}

func (m *model) updateTableRows() {
	rows := []table.Row{}
	for _, data := range m.portfolioData {
		rows = append(rows, table.Row{
			data.Timestamp.Format("2006-01-02 15:04:05"),
			fmt.Sprintf("$%.2f", data.Cash),
		})
	}
	m.table.SetRows(rows)
}

func (m model) handleAddEntry() (tea.Model, tea.Cmd) {
	var cash float64
	_, err := fmt.Sscanf(m.textInput.Value(), "%f", &cash)
	if err != nil {
		m.message = errorStyle.Render("Invalid number format")
		return m, nil
	}

	m.isAdding = false
	m.textInput.Reset()
	m.textInput.Blur()

	return m, addEntryCmd(cash)
}

// Commands and messages
type fetchDataMsg []database.PortfolioData
type errMsg error

func fetchDataCmd() tea.Msg {
	entries, err := database.GetAllPortfolios(context.Background())
	if err != nil {
		return errMsg(err)
	}

	return fetchDataMsg(entries)
}

func addEntryCmd(cash float64) tea.Cmd {
	return func() tea.Msg {
		ctx := context.Background()
		dbConn, err := database.InitDB()
		if err != nil {
			return errMsg(err)
		}
		defer dbConn.Close()
		queries := database.New(dbConn)
		_, err = queries.CreatePortfolio(ctx, database.CreatePortfolioParams{
			Cash:      cash,
			Timestamp: time.Now(),
		})
		if err != nil {
			return errMsg(err)
		}
		return fetchDataCmd()
	}
}

func main() {
	// Initialize SQLite database
	dbConn, err := database.InitDB()
	if err != nil {
		log.Fatal("Error initializing database:", err)
	}
	defer dbConn.Close()

	// Run the TUI
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		log.Fatal(err)
		os.Exit(1)
	}
}
