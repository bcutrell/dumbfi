"""
Game configuration and theme management.

Replaces the awkward hardcoded config system with flexible, extensible configuration.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from pathlib import Path


@dataclass
class Theme:
    """Visual theme configuration."""

    name: str
    background: int = 0  # Black
    grid: int = 5  # Dark Blue
    border: int = 13  # Gray
    text: int = 7  # White
    text_highlight: int = 10  # Yellow
    widget_bg: int = 1  # Navy

    # Button colors
    button_active: int = 11  # Lime
    button_hover: int = 9  # Orange
    button_inactive: int = 5  # Dark Blue

    # Graph colors
    graph_line: int = 11  # Lime
    graph_positive: int = 11  # Lime
    graph_negative: int = 8  # Red

    # UI elements
    scroll_indicator: int = 7  # White


# Predefined themes
THEMES = {
    "default": Theme(name="default"),
    "dark": Theme(
        name="dark",
        background=0,
        grid=13,
        border=5,
        text=7,
        text_highlight=12,
        widget_bg=1,
        button_active=3,
        button_hover=2,
        button_inactive=13,
        graph_line=12,
        graph_positive=3,
        graph_negative=8,
        scroll_indicator=7,
    ),
    "retro": Theme(
        name="retro",
        background=1,
        grid=5,
        border=7,
        text=10,
        text_highlight=14,
        widget_bg=2,
        button_active=9,
        button_hover=8,
        button_inactive=5,
        graph_line=9,
        graph_positive=9,
        graph_negative=14,
        scroll_indicator=15,
    ),
    "hacker": Theme(
        name="hacker",
        background=0,
        grid=13,
        border=3,
        text=3,
        text_highlight=11,
        widget_bg=0,
        button_active=11,
        button_hover=3,
        button_inactive=1,
        graph_line=3,
        graph_positive=11,
        graph_negative=8,
        scroll_indicator=3,
    ),
}


@dataclass
class GameConfig:
    """Main game configuration."""

    # Screen settings
    screen_width: int = 240
    screen_height: int = 180
    screen_fps: int = 30
    grid_size: int = 10
    show_grid: bool = True

    # Theme
    theme: Optional[Theme] = None

    def __post_init__(self):
        """Initialize defaults after construction."""
        if self.theme is None:
            self.theme = THEMES["default"]

    # Market data
    market_data_file: str = "data/sample_prices.csv"

    # Game mechanics
    start_cash: float = 1_000_000
    transaction_fee: float = 0.001  # 0.1%
    max_stocks: int = 10
    rebalance_cooldown: int = 5  # days

    # Simulation settings
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    play_speed: int = 1  # days per frame

    # Widget margins and padding
    widget_margin: int = 5
    widget_padding: int = 3

    @classmethod
    def load_theme(cls, theme_name: str) -> "GameConfig":
        """Load configuration with specified theme."""
        if theme_name not in THEMES:
            available = ", ".join(THEMES.keys())
            raise ValueError(f"Unknown theme '{theme_name}'. Available: {available}")

        config = cls()
        config.theme = THEMES[theme_name]
        return config

    @classmethod
    def from_file(cls, config_file: str) -> "GameConfig":
        """Load configuration from file (future implementation)."""
        # TODO: Implement JSON/TOML configuration loading
        return cls()

    def save_to_file(self, config_file: str) -> None:
        """Save configuration to file (future implementation)."""
        # TODO: Implement configuration saving
        pass

    def get_data_file_path(self) -> Path:
        """Get resolved path to market data file."""
        return Path(self.market_data_file)

    def validate(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []

        if self.screen_width <= 0 or self.screen_height <= 0:
            errors.append("Screen dimensions must be positive")

        if self.screen_fps <= 0:
            errors.append("FPS must be positive")

        if self.start_cash <= 0:
            errors.append("Starting cash must be positive")

        if not (0 <= self.transaction_fee <= 1):
            errors.append("Transaction fee must be between 0 and 1")

        if not self.get_data_file_path().exists():
            errors.append(f"Market data file not found: {self.market_data_file}")

        return errors

    def get_color_palette(self) -> Dict[str, int]:
        """Get color palette dictionary for easy access."""
        return {
            "background": self.theme.background,
            "grid": self.theme.grid,
            "border": self.theme.border,
            "text": self.theme.text,
            "text_highlight": self.theme.text_highlight,
            "widget_bg": self.theme.widget_bg,
            "button_active": self.theme.button_active,
            "button_hover": self.theme.button_hover,
            "button_inactive": self.theme.button_inactive,
            "graph_line": self.theme.graph_line,
            "graph_positive": self.theme.graph_positive,
            "graph_negative": self.theme.graph_negative,
            "scroll_indicator": self.theme.scroll_indicator,
        }
