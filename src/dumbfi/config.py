#
# Market Data
#

# Paths (temp)
MARKET_DATA_FILE = "sample_prices.csv"

#
# Screen settings
#
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 180
SCREEN_FPS = 30
GRID_SIZE = 10
SHOW_GRID = True

#
# Color palette (standard Pyxel palette)
#
# 0: Black     1: Navy      2: Purple    3: Green
# 4: Brown     5: DarkBlue  6: LightBlue 7: White
# 8: Red       9: Orange    10: Yellow   11: Lime
# 12: Cyan     13: Gray     14: Pink     15: Peach

# Game colors
COLOR_BACKGROUND = 0  # Black
COLOR_GRID = 5  # Dark Blue
COLOR_BORDER = 13  # Gray
COLOR_TEXT = 7  # White
COLOR_TEXT_HIGHLIGHT = 10  # Yellow
COLOR_WIDGET_BG = 1  # Navy

# Button colors
COLOR_BUTTON_ACTIVE = 11  # Lime
COLOR_BUTTON_HOVER = 9  # Orange
COLOR_BUTTON_INACTIVE = 5  # Dark Blue

# Graph colors
COLOR_GRAPH_LINE = 11  # Lime
COLOR_GRAPH_POSITIVE = 11  # Lime (for gains)
COLOR_GRAPH_NEGATIVE = 8  # Red (for losses)

# Scroll indicator
COLOR_SCROLL_INDICATOR = 7  # White

#
# Widget settings
#
WIDGET_MARGIN = 5
WIDGET_PADDING = 3

# Timeline - Centered at the top of the app
TIMELINE_HEIGHT = 4
TIMELINE_WIDTH = 220
TIMELINE_X = (SCREEN_WIDTH - TIMELINE_WIDTH) // 2
TIMELINE_Y = 10

# Play/Pause button
PLAY_BUTTON_WIDTH = 60
PLAY_BUTTON_HEIGHT = 15
PLAY_BUTTON_X = 10
PLAY_BUTTON_Y = 30

# Rebalance button
REBALANCE_BUTTON_WIDTH = 60
REBALANCE_BUTTON_HEIGHT = 15
REBALANCE_BUTTON_X = 10
REBALANCE_BUTTON_Y = 50

# Holdings list
HOLDINGS_LIST_WIDTH = 100
HOLDINGS_LIST_HEIGHT = 60
HOLDINGS_LIST_X = 10
HOLDINGS_LIST_Y = 70

# Total AUM display
AUM_WIDGET_WIDTH = 60
AUM_WIDGET_HEIGHT = 35
AUM_WIDGET_X = 170
AUM_WIDGET_Y = 30

# Total value graph
TOTAL_VALUE_GRAPH_WIDTH = 80
TOTAL_VALUE_GRAPH_HEIGHT = 60
TOTAL_VALUE_GRAPH_X = 150
TOTAL_VALUE_GRAPH_Y = 70


# Game settings - can be adjusted for different gameplay styles
GAME_START_CASH = 1000000  # Starting amount in dollars
TRANSACTION_FEE = 0.001  # 0.1% fee per trade
MAX_STOCKS = 10  # Maximum number of stocks player can hold
REBALANCE_COOLDOWN = 5  # Days between allowed rebalances

# Theme presets - easily swap between different visual themes
# To change the theme, just update these variables at the top:
CURRENT_THEME = "default"  # Options: "default", "dark", "retro", "hacker"


# Define themes as functions to allow for computed values
def apply_theme(theme_name):
    global COLOR_BACKGROUND, COLOR_GRID, COLOR_BORDER, COLOR_TEXT
    global COLOR_TEXT_HIGHLIGHT, COLOR_WIDGET_BG, COLOR_BUTTON_ACTIVE
    global COLOR_BUTTON_HOVER, COLOR_BUTTON_INACTIVE, COLOR_GRAPH_LINE
    global COLOR_GRAPH_POSITIVE, COLOR_GRAPH_NEGATIVE, COLOR_SCROLL_INDICATOR

    if theme_name == "dark":
        # Dark theme
        COLOR_BACKGROUND = 0  # Black
        COLOR_GRID = 13  # Gray
        COLOR_BORDER = 5  # Dark Blue
        COLOR_TEXT = 7  # White
        COLOR_TEXT_HIGHLIGHT = 12  # Cyan
        COLOR_WIDGET_BG = 1  # Navy
        COLOR_BUTTON_ACTIVE = 3  # Green
        COLOR_BUTTON_HOVER = 2  # Purple
        COLOR_BUTTON_INACTIVE = 13  # Gray
        COLOR_GRAPH_LINE = 12  # Cyan
        COLOR_GRAPH_POSITIVE = 3  # Green
        COLOR_GRAPH_NEGATIVE = 8  # Red
        COLOR_SCROLL_INDICATOR = 7  # White

    elif theme_name == "retro":
        # Retro theme
        COLOR_BACKGROUND = 1  # Navy
        COLOR_GRID = 5  # Dark Blue
        COLOR_BORDER = 7  # White
        COLOR_TEXT = 10  # Yellow
        COLOR_TEXT_HIGHLIGHT = 14  # Pink
        COLOR_WIDGET_BG = 2  # Purple
        COLOR_BUTTON_ACTIVE = 9  # Orange
        COLOR_BUTTON_HOVER = 8  # Red
        COLOR_BUTTON_INACTIVE = 5  # Dark Blue
        COLOR_GRAPH_LINE = 9  # Orange
        COLOR_GRAPH_POSITIVE = 9  # Orange
        COLOR_GRAPH_NEGATIVE = 14  # Pink
        COLOR_SCROLL_INDICATOR = 15  # Peach

    elif theme_name == "hacker":
        # Hacker theme
        COLOR_BACKGROUND = 0  # Black
        COLOR_GRID = 13  # Gray
        COLOR_BORDER = 3  # Green
        COLOR_TEXT = 3  # Green
        COLOR_TEXT_HIGHLIGHT = 11  # Lime
        COLOR_WIDGET_BG = 0  # Black
        COLOR_BUTTON_ACTIVE = 11  # Lime
        COLOR_BUTTON_HOVER = 3  # Green
        COLOR_BUTTON_INACTIVE = 1  # Navy
        COLOR_GRAPH_LINE = 3  # Green
        COLOR_GRAPH_POSITIVE = 11  # Lime
        COLOR_GRAPH_NEGATIVE = 8  # Red
        COLOR_SCROLL_INDICATOR = 3  # Green

    else:  # default theme
        # Default values are already set at the top level
        pass


# Apply the currently selected theme
apply_theme(CURRENT_THEME)
