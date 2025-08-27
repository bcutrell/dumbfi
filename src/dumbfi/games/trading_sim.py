"""
Trading Simulator Game

A retro-style trading simulator built with Pyxel that uses the DumbFi finance library.
Now with proper portfolio management, realistic market data, and configurable UI.
"""

import pyxel
import datetime
import random
from typing import List, Dict, Optional, Tuple

from dumbfi.finance import MarketData, Portfolio
from dumbfi.config import GameConfig, UIConfig, LayoutType
from dumbfi.widgets import (
    LineGraphWidget,
    ButtonWidget,
    TimelineWidget,
    ScrollableListWidget,
    TextBoxWidget,
)


class TradingSimulator:
    """
    Main trading simulator game using the new architecture.
    """

    def __init__(
        self,
        game_config: Optional[GameConfig] = None,
        ui_config: Optional[UIConfig] = None,
    ):
        """
        Initialize the trading simulator.

        Args:
            game_config: Game configuration (uses default if None)
            ui_config: UI layout configuration (uses standard if None)
        """
        # Load configurations
        self.config = game_config or GameConfig()
        self.ui_config = ui_config or UIConfig.from_layout_type(LayoutType.STANDARD)

        # Validate configurations
        config_errors = self.config.validate()
        layout_errors = self.ui_config.validate_layout()

        if config_errors:
            print("⚠️  Configuration warnings:", config_errors)
        if layout_errors:
            print("⚠️  Layout warnings:", layout_errors)

        # Initialize market data
        try:
            self.market_data = MarketData(str(self.config.get_data_file_path()))
            print(
                f"✅ Loaded market data: {len(self.market_data.get_available_tickers())} assets"
            )
        except Exception as e:
            print(f"❌ Failed to load market data: {e}")
            # Create dummy data for demo
            self.market_data = None

        # Initialize portfolio using the finance library
        self.portfolio = Portfolio(
            initial_cash=self.config.start_cash, name="Trading Game Portfolio"
        )

        # Game state
        self.init_game_state()

        # UI widgets
        self.widgets = []
        self.init_widgets()

        # Start pyxel
        pyxel.init(
            self.ui_config.screen_width,
            self.ui_config.screen_height,
            title="DumbFi Trading Simulator",
            fps=self.config.screen_fps,
        )
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def init_game_state(self):
        """Initialize game state variables."""
        # Timeline settings
        self.is_playing = False
        self.play_speed = self.config.play_speed
        self.start_date = datetime.datetime.strptime(
            self.config.start_date, "%Y-%m-%d"
        ).date()
        self.end_date = datetime.datetime.strptime(
            self.config.end_date, "%Y-%m-%d"
        ).date()
        self.current_date = self.start_date
        self.days_in_year = (self.end_date - self.start_date).days + 1

        # Available tickers for trading
        if self.market_data:
            self.available_tickers = self.market_data.filter_by_availability(
                min_data_points=200
            )[:20]  # Limit for UI
        else:
            # Demo tickers
            self.available_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

        # Current prices (updated during simulation)
        self.current_prices = {}
        self.update_current_prices()

        # Performance tracking
        self.portfolio_values = []  # For graphing
        self.last_rebalance_day = 0

        # Trading state
        self.selected_ticker = (
            self.available_tickers[0] if self.available_tickers else "AAPL"
        )
        self.trade_quantity = 10

    def init_widgets(self):
        """Initialize all UI widgets using the new configuration system."""
        colors = self.config.get_color_palette()

        # Timeline widget
        timeline_cfg = self.ui_config.timeline
        self.timeline_widget = TimelineWidget(
            x=timeline_cfg.x,
            y=timeline_cfg.y,
            width=timeline_cfg.width,
            height=timeline_cfg.height,
            start_date=self.start_date,
            end_date=self.end_date,
            current_date=self.current_date,
            border_color=colors["border"],
            completed_color=colors["graph_positive"],
            remaining_color=colors["border"],
            text_color=colors["text"],
            grid_size=self.config.grid_size,
            bg_color=colors["widget_bg"],
            margin=self.config.widget_margin,
            draggable=timeline_cfg.draggable,
        )
        self.widgets.append(self.timeline_widget)

        # Play/Pause button
        play_cfg = self.ui_config.play_button
        self.play_button = ButtonWidget(
            x=play_cfg.x,
            y=play_cfg.y,
            width=play_cfg.width,
            height=play_cfg.height,
            text="Play",
            callback=self.on_play_pause,
            active_color=colors["button_active"],
            hover_color=colors["button_hover"],
            inactive_color=colors["button_inactive"],
            text_color=colors["text"],
            padding=self.config.widget_padding,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
        )
        self.widgets.append(self.play_button)

        # Buy/Sell buttons (new!)
        buy_button_x = play_cfg.x + play_cfg.width + 10
        self.buy_button = ButtonWidget(
            x=buy_button_x,
            y=play_cfg.y,
            width=40,
            height=play_cfg.height,
            text="Buy",
            callback=self.on_buy,
            active_color=colors["graph_positive"],
            hover_color=colors["button_hover"],
            inactive_color=colors["button_inactive"],
            text_color=colors["text"],
            padding=self.config.widget_padding,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
        )
        self.widgets.append(self.buy_button)

        sell_button_x = buy_button_x + 45
        self.sell_button = ButtonWidget(
            x=sell_button_x,
            y=play_cfg.y,
            width=40,
            height=play_cfg.height,
            text="Sell",
            callback=self.on_sell,
            active_color=colors["graph_negative"],
            hover_color=colors["button_hover"],
            inactive_color=colors["button_inactive"],
            text_color=colors["text"],
            padding=self.config.widget_padding,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
        )
        self.widgets.append(self.sell_button)

        # Portfolio value graph
        graph_cfg = self.ui_config.portfolio_graph
        self.portfolio_graph = LineGraphWidget(
            x=graph_cfg.x,
            y=graph_cfg.y,
            width=graph_cfg.width,
            height=graph_cfg.height,
            line_color=colors["graph_line"],
            grid_size=self.config.grid_size,
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            margin=self.config.widget_margin,
            resizeable=graph_cfg.resizeable,
        )
        self.widgets.append(self.portfolio_graph)

        # Holdings list using real portfolio data
        holdings_cfg = self.ui_config.holdings_list
        self.holdings_widget = ScrollableListWidget(
            x=holdings_cfg.x,
            y=holdings_cfg.y,
            width=holdings_cfg.width,
            height=holdings_cfg.height,
            positions=self.get_position_list(),
            text_color=colors["text"],
            highlight_color=colors["text_highlight"],
            scroll_indicator_color=colors["scroll_indicator"],
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            grid_size=self.config.grid_size,
            margin=self.config.widget_margin,
        )
        self.widgets.append(self.holdings_widget)

        # Portfolio value display
        aum_cfg = self.ui_config.aum_display
        self.aum_widget = TextBoxWidget(
            x=aum_cfg.x,
            y=aum_cfg.y,
            width=aum_cfg.width,
            height=aum_cfg.height,
            total_aum=self.portfolio.get_total_value(),
            text_color=colors["text"],
            highlight_color=colors["text_highlight"],
            title="PORTFOLIO VALUE",
            border_color=colors["border"],
            bg_color=colors["widget_bg"],
            grid_size=self.config.grid_size,
            margin=self.config.widget_margin,
        )
        self.widgets.append(self.aum_widget)

    def get_position_list(self) -> List[Tuple[str, float]]:
        """Get current portfolio positions for display."""
        positions = []

        for ticker, position in self.portfolio.positions.items():
            market_value = position.market_value or position.cost_basis
            positions.append((ticker, market_value))

        # Add cash position
        positions.append(("CASH", self.portfolio.cash))

        return positions

    def update_current_prices(self):
        """Update current prices from market data."""
        if not self.market_data:
            # Use random prices for demo
            for ticker in self.available_tickers:
                if ticker not in self.current_prices:
                    self.current_prices[ticker] = 100.0  # Base price
                # Random walk
                change = random.uniform(-0.02, 0.02)
                self.current_prices[ticker] *= 1 + change
            return

        # Get real prices from market data
        date_str = self.current_date.strftime("%Y-%m-%d")

        for ticker in self.available_tickers:
            price = self.market_data.get_price(date_str, ticker)
            if price is not None:
                self.current_prices[ticker] = price

        # Update portfolio with current prices
        self.portfolio.update_prices(self.current_prices)

    def on_play_pause(self):
        """Toggle play/pause state."""
        self.is_playing = not self.is_playing
        self.play_button.set_text("Pause" if self.is_playing else "Play")

    def on_buy(self):
        """Handle buy order."""
        if self.selected_ticker in self.current_prices:
            price = self.current_prices[self.selected_ticker]
            transaction_cost = price * self.trade_quantity * self.config.transaction_fee

            success = self.portfolio.add_position(
                self.selected_ticker, self.trade_quantity, price, transaction_cost
            )

            if success:
                print(
                    f"✅ Bought {self.trade_quantity} shares of {self.selected_ticker} @ ${price:.2f}"
                )
                self.update_displays()
            else:
                print(f"❌ Buy order failed - insufficient funds")

    def on_sell(self):
        """Handle sell order."""
        if self.selected_ticker in self.portfolio.positions:
            price = self.current_prices.get(self.selected_ticker, 0)
            transaction_cost = price * self.trade_quantity * self.config.transaction_fee

            success = self.portfolio.add_position(
                self.selected_ticker,
                -self.trade_quantity,  # Negative for sell
                price,
                transaction_cost,
            )

            if success:
                print(
                    f"✅ Sold {self.trade_quantity} shares of {self.selected_ticker} @ ${price:.2f}"
                )
                self.update_displays()
            else:
                print(f"❌ Sell order failed - insufficient shares")

    def update_displays(self):
        """Update all display widgets with current data."""
        # Update portfolio value display
        self.aum_widget.total_aum = self.portfolio.get_total_value()

        # Update holdings list
        self.holdings_widget.positions = self.get_position_list()

        # Record performance snapshot
        self.portfolio.record_snapshot(
            datetime.datetime.combine(self.current_date, datetime.time())
        )

    def update(self):
        """Update game state (called every frame)."""
        # Handle simulation progression
        if self.is_playing and pyxel.frame_count % 30 == 0:  # Slower than original
            # Advance date
            new_date = self.current_date + datetime.timedelta(days=self.play_speed)
            if new_date <= self.end_date:
                self.current_date = new_date
                self.timeline_widget.current_date = self.current_date

                # Update market prices
                self.update_current_prices()

                # Update displays
                self.update_displays()

                # Add portfolio value to graph
                current_value = self.portfolio.get_total_value()
                normalized_value = (
                    current_value / self.config.start_cash
                ) * 100  # Normalize to percentage
                self.portfolio_graph.add_data_point(normalized_value)

        # Update all widgets
        for widget in self.widgets:
            widget.update()

        # Handle widget interactions
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for widget in reversed(self.widgets):
                if (
                    hasattr(widget, "resizeable")
                    and widget.resizeable
                    and widget.start_resize(pyxel.mouse_x, pyxel.mouse_y)
                ):
                    break
                elif (
                    hasattr(widget, "draggable")
                    and widget.draggable
                    and widget.start_drag(pyxel.mouse_x, pyxel.mouse_y)
                ):
                    break

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            for widget in self.widgets:
                if hasattr(widget, "resizing") and widget.resizing:
                    widget.update_resize(
                        pyxel.mouse_x,
                        pyxel.mouse_y,
                        self.ui_config.screen_width,
                        self.ui_config.screen_height,
                    )
                elif hasattr(widget, "dragging") and widget.dragging:
                    widget.update_drag(
                        pyxel.mouse_x,
                        pyxel.mouse_y,
                        self.ui_config.screen_width,
                        self.ui_config.screen_height,
                    )

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            for widget in self.widgets:
                if hasattr(widget, "end_drag"):
                    widget.end_drag()
                if hasattr(widget, "end_resize"):
                    widget.end_resize()

        # Keyboard shortcuts
        if pyxel.btnp(pyxel.KEY_G):
            self.config.show_grid = not self.config.show_grid

        if pyxel.btnp(pyxel.KEY_T):
            # Cycle through themes
            theme_names = ["default", "dark", "retro", "hacker"]
            current_idx = theme_names.index(self.config.theme.name)
            next_idx = (current_idx + 1) % len(theme_names)
            self.config = GameConfig.load_theme(theme_names[next_idx])

        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            # Print final portfolio summary
            summary = self.portfolio.summary()
            print(f"\n🎮 Game Over! Final Portfolio Summary:")
            print(f"   💰 Final Value: ${summary['total_value']:,.2f}")
            print(f"   📈 Total Return: {summary['total_return']:.2f}%")
            print(f"   🏦 Cash Remaining: ${summary['cash']:,.2f}")
            print(f"   📊 Positions: {summary['num_positions']}")
            pyxel.quit()

    def draw(self):
        """Render the game (called every frame)."""
        colors = self.config.get_color_palette()
        pyxel.cls(colors["background"])

        # Draw grid if enabled
        if self.config.show_grid:
            self.draw_grid(colors["grid"])

        # Draw all widgets
        for widget in self.widgets:
            widget.draw()

        # Draw game info overlay
        self.draw_info_overlay(colors)

        # Draw debug info if enabled
        if hasattr(self.config, "debug") and self.config.debug:
            self.draw_debug_info(colors)

    def draw_grid(self, grid_color: int):
        """Draw grid dots."""
        for x in range(0, self.ui_config.screen_width, self.config.grid_size):
            for y in range(0, self.ui_config.screen_height, self.config.grid_size):
                pyxel.pset(x, y, grid_color)

    def draw_info_overlay(self, colors: Dict[str, int]):
        """Draw game information overlay."""
        # Current date
        date_str = self.current_date.strftime("%Y-%m-%d")
        pyxel.text(5, 5, f"Date: {date_str}", colors["text"])

        # Selected ticker and trade size
        info_y = self.ui_config.screen_height - 25
        pyxel.text(5, info_y, f"Selected: {self.selected_ticker}", colors["text"])
        pyxel.text(5, info_y + 8, f"Quantity: {self.trade_quantity}", colors["text"])

        # Current price
        if self.selected_ticker in self.current_prices:
            price = self.current_prices[self.selected_ticker]
            pyxel.text(5, info_y + 16, f"Price: ${price:.2f}", colors["text"])

        # Portfolio performance
        total_return = self.portfolio.get_total_return()
        return_color = (
            colors["graph_positive"] if total_return >= 0 else colors["graph_negative"]
        )
        return_text = f"Return: {total_return:+.1f}%"
        pyxel.text(
            self.ui_config.screen_width - len(return_text) * 4 - 5,
            5,
            return_text,
            return_color,
        )

    def draw_debug_info(self, colors: Dict[str, int]):
        """Draw debug information."""
        coord_text = f"({pyxel.mouse_x}, {pyxel.mouse_y})"
        pyxel.text(
            pyxel.mouse_x + 10, pyxel.mouse_y - 10, coord_text, colors["text_highlight"]
        )
        pyxel.pset(pyxel.mouse_x, pyxel.mouse_y, colors["graph_positive"])


# Standalone execution
def main():
    """Run the trading simulator with default configuration."""
    print("🎮 Starting DumbFi Trading Simulator...")

    # Choose configuration
    config = GameConfig.load_theme("retro")  # Try the retro theme!
    ui_config = UIConfig.from_layout_type(LayoutType.STANDARD)  # Use standard layout

    # Start the game
    game = TradingSimulator(config, ui_config)


if __name__ == "__main__":
    main()
