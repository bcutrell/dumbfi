"""
Common utilities for DumbFi applications.

Provides reusable functions for date handling, price formatting, widget creation,
and other common operations used across games and notebooks.
"""

import datetime
import random
import logging
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path

import pyxel

from dumbfi.finance import MarketData, Portfolio
from dumbfi.config import GameConfig, UIConfig
from dumbfi.widgets import (
    LineGraphWidget,
    ButtonWidget,
    TimelineWidget,
    ScrollableListWidget,
    TextBoxWidget,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """Encapsulates all game state in a single object."""

    current_date: datetime.date
    is_playing: bool = False
    play_speed: int = 1
    selected_ticker: str = "AAPL"
    trade_quantity: int = 10
    current_prices: Dict[str, float] = None
    last_rebalance_day: int = 0

    def __post_init__(self):
        if self.current_prices is None:
            self.current_prices = {}


class DateUtils:
    """Utility functions for date operations."""

    @staticmethod
    def parse_date(date_str: str) -> datetime.date:
        """Parse date string to date object."""
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def format_date(date_obj: datetime.date) -> str:
        """Format date object to string."""
        return date_obj.strftime("%Y-%m-%d")

    @staticmethod
    def advance_date(current_date: datetime.date, days: int = 1) -> datetime.date:
        """Advance date by specified number of days."""
        return current_date + datetime.timedelta(days=days)

    @staticmethod
    def days_between(start_date: datetime.date, end_date: datetime.date) -> int:
        """Calculate days between two dates."""
        return (end_date - start_date).days + 1

    @staticmethod
    def is_weekend(date_obj: datetime.date) -> bool:
        """Check if date is weekend."""
        return date_obj.weekday() >= 5  # Saturday = 5, Sunday = 6


class FormatUtils:
    """Utility functions for formatting values."""

    @staticmethod
    def format_currency(value: float, precision: int = 2) -> str:
        """Format value as currency."""
        return f"${value:,.{precision}f}"

    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """Format value as percentage."""
        return f"{value:.{precision}f}%"

    @staticmethod
    def format_return(value: float, precision: int = 1) -> str:
        """Format return with +/- sign."""
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.{precision}f}%"

    @staticmethod
    def truncate_text(text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis."""
        return text[: max_length - 3] + "..." if len(text) > max_length else text


class PriceUtils:
    """Utility functions for price operations."""

    @staticmethod
    def update_prices_from_market(
        market_data: MarketData, date_str: str, tickers: List[str]
    ) -> Dict[str, float]:
        """Update prices from market data for given date."""
        prices = {}
        for ticker in tickers:
            price = market_data.get_price(date_str, ticker)
            if price is not None:
                prices[ticker] = price
        return prices

    @staticmethod
    def generate_random_prices(
        tickers: List[str],
        base_prices: Optional[Dict[str, float]] = None,
        volatility: float = 0.02,
    ) -> Dict[str, float]:
        """Generate random prices with volatility."""
        prices = {}
        for ticker in tickers:
            base_price = base_prices.get(ticker, 100.0) if base_prices else 100.0
            change = random.uniform(-volatility, volatility)
            prices[ticker] = base_price * (1 + change)
        return prices

    @staticmethod
    def calculate_transaction_cost(
        quantity: int, price: float, fee_rate: float
    ) -> float:
        """Calculate transaction cost."""
        return abs(quantity) * price * fee_rate


class WidgetFactory:
    """Factory for creating configured widgets."""

    @staticmethod
    def create_timeline(
        config: UIConfig,
        game_config: GameConfig,
        start_date: datetime.date,
        end_date: datetime.date,
        current_date: datetime.date,
    ) -> TimelineWidget:
        """Create configured timeline widget."""
        timeline_cfg = config.timeline
        colors = game_config.get_color_palette()

        return TimelineWidget(
            x=timeline_cfg.x,
            y=timeline_cfg.y,
            width=timeline_cfg.width,
            height=timeline_cfg.height,
            start_date=start_date,
            end_date=end_date,
            current_date=current_date,
            border_color=colors["border"],
            completed_color=colors["graph_positive"],
            remaining_color=colors["border"],
            text_color=colors["text"],
            grid_size=game_config.grid_size,
            bg_color=colors["widget_bg"],
            margin=game_config.widget_margin,
            draggable=timeline_cfg.draggable,
        )

    @staticmethod
    def create_button(
        config: UIConfig, game_config: GameConfig, widget_name: str, text: str, callback
    ) -> ButtonWidget:
        """Create configured button widget."""
        button_cfg = getattr(config, widget_name)
        colors = game_config.get_color_palette()

        return ButtonWidget(
            x=button_cfg.x,
            y=button_cfg.y,
            width=button_cfg.width,
            height=button_cfg.height,
            text=text,
            callback=callback,
            active_color=colors["button_active"],
            hover_color=colors["button_hover"],
            inactive_color=colors["button_inactive"],
            text_color=colors["text"],
            padding=game_config.widget_padding,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
        )

    @staticmethod
    def create_custom_button(
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback,
        game_config: GameConfig,
        color_override: Optional[str] = None,
    ) -> ButtonWidget:
        """Create custom positioned button."""
        colors = game_config.get_color_palette()
        active_color = colors.get(color_override, colors["button_active"])

        return ButtonWidget(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            callback=callback,
            active_color=active_color,
            hover_color=colors["button_hover"],
            inactive_color=colors["button_inactive"],
            text_color=colors["text"],
            padding=game_config.widget_padding,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
        )

    @staticmethod
    def create_portfolio_graph(
        config: UIConfig, game_config: GameConfig
    ) -> LineGraphWidget:
        """Create configured portfolio graph widget."""
        graph_cfg = config.portfolio_graph
        colors = game_config.get_color_palette()

        return LineGraphWidget(
            x=graph_cfg.x,
            y=graph_cfg.y,
            width=graph_cfg.width,
            height=graph_cfg.height,
            line_color=colors["graph_line"],
            grid_size=game_config.grid_size,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            margin=game_config.widget_margin,
            resizeable=graph_cfg.resizeable,
        )

    @staticmethod
    def create_holdings_list(
        config: UIConfig, game_config: GameConfig, positions: List[Tuple[str, float]]
    ) -> ScrollableListWidget:
        """Create configured holdings list widget."""
        holdings_cfg = config.holdings_list
        colors = game_config.get_color_palette()

        return ScrollableListWidget(
            x=holdings_cfg.x,
            y=holdings_cfg.y,
            width=holdings_cfg.width,
            height=holdings_cfg.height,
            positions=positions,
            text_color=colors["text"],
            highlight_color=colors["text_highlight"],
            scroll_indicator_color=colors["scroll_indicator"],
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            grid_size=game_config.grid_size,
            margin=game_config.widget_margin,
        )

    @staticmethod
    def create_value_display(
        config: UIConfig, game_config: GameConfig, value: float, title: str = "VALUE"
    ) -> TextBoxWidget:
        """Create configured value display widget."""
        aum_cfg = config.aum_display
        colors = game_config.get_color_palette()

        return TextBoxWidget(
            x=aum_cfg.x,
            y=aum_cfg.y,
            width=aum_cfg.width,
            height=aum_cfg.height,
            total_aum=value,
            text_color=colors["text"],
            highlight_color=colors["text_highlight"],
            title=title,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            grid_size=game_config.grid_size,
            margin=game_config.widget_margin,
        )


class WidgetManager:
    """Manages widget collections and interactions."""

    def __init__(self, widgets: List[Any]):
        self.widgets = widgets

    def update_all(self) -> None:
        """Update all widgets."""
        for widget in self.widgets:
            widget.update()

    def draw_all(self) -> None:
        """Draw all widgets."""
        for widget in self.widgets:
            widget.draw()

    def handle_mouse_press(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle mouse press events. Returns True if handled."""
        for widget in reversed(self.widgets):
            if (
                hasattr(widget, "resizeable")
                and widget.resizeable
                and widget.start_resize(mouse_x, mouse_y)
            ):
                return True
            elif (
                hasattr(widget, "draggable")
                and widget.draggable
                and widget.start_drag(mouse_x, mouse_y)
            ):
                return True
        return False

    def handle_mouse_drag(
        self, mouse_x: int, mouse_y: int, screen_width: int, screen_height: int
    ) -> None:
        """Handle mouse drag events."""
        for widget in self.widgets:
            if hasattr(widget, "resizing") and widget.resizing:
                widget.update_resize(mouse_x, mouse_y, screen_width, screen_height)
            elif hasattr(widget, "dragging") and widget.dragging:
                widget.update_drag(mouse_x, mouse_y, screen_width, screen_height)

    def handle_mouse_release(self) -> None:
        """Handle mouse release events."""
        for widget in self.widgets:
            if hasattr(widget, "end_drag"):
                widget.end_drag()
            if hasattr(widget, "end_resize"):
                widget.end_resize()

    def get_widget(self, index: int) -> Any:
        """Get widget by index."""
        return self.widgets[index] if 0 <= index < len(self.widgets) else None

    def find_widget_by_type(self, widget_type: type) -> Optional[Any]:
        """Find first widget of specified type."""
        return next((w for w in self.widgets if isinstance(w, widget_type)), None)


class MarketDataManager:
    """Manages market data loading and price updates."""

    def __init__(self, config: GameConfig):
        self.config = config
        self.market_data: Optional[MarketData] = None
        self.available_tickers: List[str] = []
        self._load_market_data()

    def _load_market_data(self) -> None:
        """Load market data from configuration."""
        try:
            data_path = self.config.get_data_file_path()
            if data_path.exists():
                self.market_data = MarketData(str(data_path))
                self.available_tickers = self.market_data.filter_by_availability(
                    min_data_points=200
                )[:20]
                logger.info(
                    f"Loaded market data: {len(self.available_tickers)} tickers"
                )
            else:
                logger.warning(f"Market data file not found: {data_path}")
                self._use_demo_data()
        except Exception as e:
            logger.error(f"Failed to load market data: {e}")
            self._use_demo_data()

    def _use_demo_data(self) -> None:
        """Use demo tickers when real data unavailable."""
        self.available_tickers = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "TSLA",
            "AMZN",
            "NVDA",
            "META",
            "BRK.B",
        ]
        logger.info("Using demo tickers")

    def get_prices_for_date(self, date_str: str) -> Dict[str, float]:
        """Get prices for all available tickers on a specific date."""
        if self.market_data:
            return PriceUtils.update_prices_from_market(
                self.market_data, date_str, self.available_tickers
            )
        else:
            # Generate random prices for demo
            return PriceUtils.generate_random_prices(self.available_tickers)

    def has_real_data(self) -> bool:
        """Check if we have real market data."""
        return self.market_data is not None


class GameRenderer:
    """Handles game rendering operations."""

    @staticmethod
    def clear_screen(color: int) -> None:
        """Clear screen with specified color."""
        pyxel.cls(color)

    @staticmethod
    def draw_grid(width: int, height: int, grid_size: int, grid_color: int) -> None:
        """Draw grid dots on screen."""
        for x in range(0, width, grid_size):
            for y in range(0, height, grid_size):
                pyxel.pset(x, y, grid_color)

    @staticmethod
    def draw_text(x: int, y: int, text: str, color: int) -> None:
        """Draw text at position."""
        pyxel.text(x, y, text, color)

    @staticmethod
    def draw_info_overlay(
        game_state: GameState,
        portfolio: Portfolio,
        screen_width: int,
        screen_height: int,
        colors: Dict[str, int],
    ) -> None:
        """Draw game information overlay."""
        # Current date
        date_str = DateUtils.format_date(game_state.current_date)
        GameRenderer.draw_text(5, 5, f"Date: {date_str}", colors["text"])

        # Trading info
        info_y = screen_height - 35
        GameRenderer.draw_text(
            5, info_y, f"Selected: {game_state.selected_ticker}", colors["text"]
        )
        GameRenderer.draw_text(
            5, info_y + 8, f"Quantity: {game_state.trade_quantity}", colors["text"]
        )

        # Current price
        if game_state.selected_ticker in game_state.current_prices:
            price = game_state.current_prices[game_state.selected_ticker]
            price_text = f"Price: {FormatUtils.format_currency(price)}"
            GameRenderer.draw_text(5, info_y + 16, price_text, colors["text"])

        # Portfolio performance
        total_return = portfolio.get_total_return()
        return_color = (
            colors["graph_positive"] if total_return >= 0 else colors["graph_negative"]
        )
        return_text = f"Return: {FormatUtils.format_return(total_return)}"
        text_x = screen_width - len(return_text) * 4 - 5
        GameRenderer.draw_text(text_x, 5, return_text, return_color)

    @staticmethod
    def draw_debug_info(mouse_x: int, mouse_y: int, colors: Dict[str, int]) -> None:
        """Draw debug information."""
        coord_text = f"({mouse_x}, {mouse_y})"
        GameRenderer.draw_text(
            mouse_x + 10, mouse_y - 10, coord_text, colors["text_highlight"]
        )
        pyxel.pset(mouse_x, mouse_y, colors["graph_positive"])


class ConfigValidator:
    """Validates and fixes configuration issues."""

    @staticmethod
    def validate_and_fix_config(
        config: GameConfig, ui_config: UIConfig
    ) -> Tuple[List[str], List[str]]:
        """Validate configurations and return warnings."""
        config_warnings = config.validate()
        layout_warnings = ui_config.validate_layout()

        # Log warnings
        for warning in config_warnings:
            logger.warning(f"Config: {warning}")
        for warning in layout_warnings:
            logger.warning(f"Layout: {warning}")

        return config_warnings, layout_warnings

    @staticmethod
    def auto_fix_data_path(config: GameConfig) -> GameConfig:
        """Auto-fix data path if needed."""
        data_path = config.get_data_file_path()
        if not data_path.exists():
            # Try alternative paths
            alternatives = [
                "data/sample_prices.csv",
                "data/prices.csv",
                "sample_prices.csv",
            ]

            for alt_path in alternatives:
                if Path(alt_path).exists():
                    config.market_data_file = alt_path
                    logger.info(f"Auto-fixed data path to: {alt_path}")
                    break

        return config


class PortfolioHelper:
    """Helper functions for portfolio operations."""

    @staticmethod
    def get_display_positions(portfolio: Portfolio) -> List[Tuple[str, float]]:
        """Get portfolio positions formatted for display."""
        positions = []

        # Add stock positions
        for ticker, position in portfolio.positions.items():
            market_value = position.market_value or position.cost_basis
            positions.append((ticker, market_value))

        # Add cash position
        positions.append(("CASH", portfolio.cash))

        return positions

    @staticmethod
    def execute_trade(
        portfolio: Portfolio, ticker: str, quantity: int, price: float, fee_rate: float
    ) -> bool:
        """Execute a trade with proper error handling."""
        try:
            transaction_cost = PriceUtils.calculate_transaction_cost(
                quantity, price, fee_rate
            )
            success = portfolio.add_position(ticker, quantity, price, transaction_cost)

            action = "Bought" if quantity > 0 else "Sold"
            if success:
                logger.info(
                    f"{action} {abs(quantity)} shares of {ticker} @ {FormatUtils.format_currency(price)}"
                )
            else:
                logger.warning(
                    f"Trade failed: {action} {abs(quantity)} shares of {ticker}"
                )

            return success
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False

    @staticmethod
    def update_portfolio_displays(portfolio: Portfolio, widgets: WidgetManager) -> None:
        """Update all portfolio-related displays."""
        # Update value display
        value_widget = widgets.find_widget_by_type(TextBoxWidget)
        if value_widget:
            value_widget.total_aum = portfolio.get_total_value()

        # Update holdings list
        holdings_widget = widgets.find_widget_by_type(ScrollableListWidget)
        if holdings_widget:
            holdings_widget.positions = PortfolioHelper.get_display_positions(portfolio)

        # Record performance snapshot
        portfolio.record_snapshot()


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_and_validate_configs(
    theme: str = "default", layout: str = "standard"
) -> Tuple[GameConfig, UIConfig]:
    """Load and validate configurations with auto-fixing."""
    from dumbfi.config import LayoutType

    # Load configurations
    game_config = GameConfig.load_theme(theme)
    ui_config = UIConfig.from_layout_type(LayoutType(layout))

    # Auto-fix common issues
    game_config = ConfigValidator.auto_fix_data_path(game_config)

    # Validate and warn about issues
    ConfigValidator.validate_and_fix_config(game_config, ui_config)

    return game_config, ui_config
