"""
Configuration system for DumbFi games and applications.

Provides GameConfig, UIConfig, and LayoutType for consistent configuration
across games and notebooks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path


class LayoutType(Enum):
    """Predefined UI layout types."""

    STANDARD = "standard"
    COMPACT = "compact"
    WIDESCREEN = "widescreen"


@dataclass
class WidgetConfig:
    """Configuration for a single widget."""

    x: int
    y: int
    width: int
    height: int
    draggable: bool = True
    resizeable: bool = False


@dataclass
class ThemeConfig:
    """Color theme configuration using Pyxel palette (0-15)."""

    name: str
    background: int
    grid: int
    border: int
    text: int
    text_highlight: int
    widget_bg: int
    button_active: int
    button_hover: int
    button_inactive: int
    graph_line: int
    graph_positive: int
    graph_negative: int
    scroll_indicator: int


# Predefined themes
THEMES: Dict[str, ThemeConfig] = {
    "default": ThemeConfig(
        name="default",
        background=0,  # Black
        grid=5,  # Dark Blue
        border=13,  # Gray
        text=7,  # White
        text_highlight=10,  # Yellow
        widget_bg=1,  # Navy
        button_active=11,  # Lime
        button_hover=9,  # Orange
        button_inactive=5,  # Dark Blue
        graph_line=11,  # Lime
        graph_positive=11,  # Lime
        graph_negative=8,  # Red
        scroll_indicator=7,  # White
    ),
    "dark": ThemeConfig(
        name="dark",
        background=0,
        grid=13,
        border=5,
        text=7,
        text_highlight=12,  # Cyan
        widget_bg=1,
        button_active=3,  # Green
        button_hover=2,  # Purple
        button_inactive=13,
        graph_line=12,
        graph_positive=3,
        graph_negative=8,
        scroll_indicator=7,
    ),
    "retro": ThemeConfig(
        name="retro",
        background=1,  # Navy
        grid=5,
        border=7,  # White
        text=10,  # Yellow
        text_highlight=14,  # Pink
        widget_bg=2,  # Purple
        button_active=9,  # Orange
        button_hover=8,  # Red
        button_inactive=5,
        graph_line=9,
        graph_positive=9,
        graph_negative=14,
        scroll_indicator=15,  # Peach
    ),
    "hacker": ThemeConfig(
        name="hacker",
        background=0,
        grid=13,
        border=3,  # Green
        text=3,
        text_highlight=11,  # Lime
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
    """Game configuration with screen settings, colors, and game parameters."""

    # Screen settings
    screen_width: int = 240
    screen_height: int = 180
    screen_fps: int = 30
    grid_size: int = 10
    show_grid: bool = True

    # Game settings
    start_cash: float = 1_000_000
    transaction_fee: float = 0.001  # 0.1% per trade
    max_stocks: int = 10
    rebalance_cooldown: int = 5  # Days between rebalances
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    play_speed: int = 1

    # Widget settings
    widget_margin: int = 5
    widget_padding: int = 3

    # Data file - relative to repo root
    market_data_file: str = "../data/sample_prices.csv"

    # Theme
    theme: ThemeConfig = field(default_factory=lambda: THEMES["default"])

    def get_color_palette(self) -> Dict[str, int]:
        """Get current theme colors as dictionary."""
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

    def get_data_file_path(self) -> Path:
        """Get path to market data file."""
        return Path(self.market_data_file)

    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings."""
        warnings = []

        if self.screen_width < 160:
            warnings.append("Screen width too small, may cause layout issues")
        if self.screen_height < 120:
            warnings.append("Screen height too small, may cause layout issues")
        if self.start_cash <= 0:
            warnings.append("Start cash should be positive")
        if self.transaction_fee < 0 or self.transaction_fee > 0.1:
            warnings.append("Transaction fee should be between 0 and 10%")

        return warnings

    @classmethod
    def load_theme(cls, theme_name: str) -> "GameConfig":
        """Load configuration with specified theme."""
        theme = THEMES.get(theme_name, THEMES["default"])
        return cls(theme=theme)


@dataclass
class UIConfig:
    """UI layout configuration with widget positions."""

    screen_width: int = 240
    screen_height: int = 180

    # Widget configurations
    timeline: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=10, y=10, width=220, height=4, draggable=False
        )
    )
    play_button: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=10, y=30, width=60, height=15, draggable=False
        )
    )
    rebalance_button: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=10, y=50, width=60, height=15, draggable=False
        )
    )
    portfolio_graph: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=150, y=70, width=80, height=60, draggable=True, resizeable=True
        )
    )
    holdings_list: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=10, y=70, width=100, height=60, draggable=True
        )
    )
    aum_display: WidgetConfig = field(
        default_factory=lambda: WidgetConfig(
            x=170, y=30, width=60, height=35, draggable=True
        )
    )

    @classmethod
    def from_layout_type(cls, layout_type: LayoutType) -> "UIConfig":
        """Create UIConfig from predefined layout type."""
        if layout_type == LayoutType.COMPACT:
            return cls(
                screen_width=200,
                screen_height=150,
                timeline=WidgetConfig(x=5, y=5, width=190, height=3, draggable=False),
                play_button=WidgetConfig(x=5, y=15, width=50, height=12, draggable=False),
                rebalance_button=WidgetConfig(x=60, y=15, width=50, height=12, draggable=False),
                portfolio_graph=WidgetConfig(x=120, y=50, width=70, height=50, draggable=True, resizeable=True),
                holdings_list=WidgetConfig(x=5, y=50, width=80, height=50, draggable=True),
                aum_display=WidgetConfig(x=140, y=15, width=55, height=30, draggable=True),
            )
        elif layout_type == LayoutType.WIDESCREEN:
            return cls(
                screen_width=320,
                screen_height=180,
                timeline=WidgetConfig(x=10, y=10, width=300, height=4, draggable=False),
                play_button=WidgetConfig(x=10, y=30, width=70, height=15, draggable=False),
                rebalance_button=WidgetConfig(x=90, y=30, width=70, height=15, draggable=False),
                portfolio_graph=WidgetConfig(x=220, y=60, width=90, height=70, draggable=True, resizeable=True),
                holdings_list=WidgetConfig(x=10, y=60, width=120, height=70, draggable=True),
                aum_display=WidgetConfig(x=240, y=30, width=70, height=25, draggable=True),
            )
        else:  # STANDARD
            return cls()

    def validate_layout(self) -> List[str]:
        """Validate layout configuration and return list of warnings."""
        warnings = []

        # Check widgets fit within screen bounds
        widgets = [
            ("timeline", self.timeline),
            ("play_button", self.play_button),
            ("rebalance_button", self.rebalance_button),
            ("portfolio_graph", self.portfolio_graph),
            ("holdings_list", self.holdings_list),
            ("aum_display", self.aum_display),
        ]

        for name, widget in widgets:
            if widget.x + widget.width > self.screen_width:
                warnings.append(f"{name} extends beyond screen width")
            if widget.y + widget.height > self.screen_height:
                warnings.append(f"{name} extends beyond screen height")
            if widget.x < 0 or widget.y < 0:
                warnings.append(f"{name} has negative position")

        return warnings
