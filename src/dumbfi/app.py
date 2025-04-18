import pyxel
import datetime
import random

from dumbfi._core import get_prices
from dumbfi import config
from dumbfi.widgets import (
    LineGraphWidget,
    ButtonWidget,
    TimelineWidget,
    ScrollableListWidget,
    TextBoxWidget,
)


class App:
    def __init__(self):
        self.width = config.SCREEN_WIDTH
        self.height = config.SCREEN_HEIGHT
        self.fps = config.SCREEN_FPS
        self.grid_size = config.GRID_SIZE
        self.show_grid = config.SHOW_GRID
        self.bg_color = config.COLOR_BACKGROUND
        self.grid_color = config.COLOR_GRID

        self.init_game_state()

        self.widgets = []
        self.init_widgets()

        # placeholder for _core functions
        symbols = ["AAPL", "MSFT", "GOOG"]
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        prices = get_prices(symbols, start_date, end_date)
        assert prices is None # TODO

        # Start pyxel engine
        pyxel.init(self.width, self.height, title="dumbfi", fps=self.fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)


    def init_game_state(self):
        """Initialize game state variables"""
        # Timeline settings
        self.is_playing = False
        self.play_speed = 1  # days per frame
        self.start_date = datetime.date(2024, 1, 1)
        self.end_date = datetime.date(2024, 12, 31)
        self.current_date = self.start_date
        self.days_in_year = (self.end_date - self.start_date).days + 1

        # Portfolio data
        self.total_aum = 1000000
        self.positions = None
        # [
        #     ("AAPL", 200000),
        #     ("BTC", 200000),
        #     ("IBM", 600000),
        #     ("TSLA", 50000),
        #     ("MSFT", 75000),
        #     ("AMZN", 30000),
        #     ("GOOG", 45000),
        # ]

    def init_widgets(self):
        """Initialize all UI widgets with config values"""
        # Portfolio value graph
        self.total_value_line_graph = LineGraphWidget(
            x=config.TOTAL_VALUE_GRAPH_X,
            y=config.TOTAL_VALUE_GRAPH_Y,
            width=config.TOTAL_VALUE_GRAPH_WIDTH,
            height=config.TOTAL_VALUE_GRAPH_HEIGHT,
            line_color=config.COLOR_GRAPH_LINE,
            grid_size=config.GRID_SIZE,
            border_color=config.COLOR_BORDER,
            bg_color=config.COLOR_WIDGET_BG,
            margin=config.WIDGET_MARGIN,
        )
        self.widgets.append(self.total_value_line_graph)

        # Rebalance button
        self.rebalance_button = ButtonWidget(
            x=config.REBALANCE_BUTTON_X,
            y=config.REBALANCE_BUTTON_Y,
            width=config.REBALANCE_BUTTON_WIDTH,
            height=config.REBALANCE_BUTTON_HEIGHT,
            text="Rebalance",
            callback=self.handle_rebalance,
            active_color=config.COLOR_BUTTON_ACTIVE,
            hover_color=config.COLOR_BUTTON_HOVER,
            inactive_color=config.COLOR_BUTTON_INACTIVE,
            text_color=config.COLOR_TEXT,
            padding=config.WIDGET_PADDING,
            border_color=config.COLOR_BORDER,
            bg_color=config.COLOR_WIDGET_BG,
        )
        self.widgets.append(self.rebalance_button)

        # Play/Pause button
        self.play_button = ButtonWidget(
            x=10,
            y=30,
            width=60,
            height=15,
            text="Play",
            callback=self.on_play_pause,
            active_color=config.COLOR_BUTTON_ACTIVE,
            hover_color=config.COLOR_BUTTON_HOVER,
            inactive_color=config.COLOR_BUTTON_INACTIVE,
            text_color=config.COLOR_TEXT,
            padding=config.WIDGET_PADDING,
            border_color=config.COLOR_BORDER,
            bg_color=config.COLOR_WIDGET_BG,
        )
        self.widgets.append(self.play_button)

        # Timeline
        self.timeline_widget = TimelineWidget(
            x=config.TIMELINE_X,
            y=config.TIMELINE_Y,
            width=config.TIMELINE_WIDTH,
            height=config.TIMELINE_HEIGHT,
            start_date=self.start_date,
            end_date=self.end_date,
            current_date=self.current_date,
            border_color=config.COLOR_BORDER,
            completed_color=config.COLOR_GRAPH_POSITIVE,
            remaining_color=config.COLOR_BORDER,
            text_color=config.COLOR_TEXT,
            grid_size=config.GRID_SIZE,
            bg_color=config.COLOR_WIDGET_BG,
            margin=config.WIDGET_MARGIN,
        )
        self.widgets.append(self.timeline_widget)

        # Holdings list
        self.holdings_widget = ScrollableListWidget(
            x=config.HOLDINGS_LIST_X,
            y=config.HOLDINGS_LIST_Y,
            width=config.HOLDINGS_LIST_WIDTH,
            height=config.HOLDINGS_LIST_HEIGHT,
            positions=self.positions,
            text_color=config.COLOR_TEXT,
            highlight_color=config.COLOR_TEXT_HIGHLIGHT,
            scroll_indicator_color=config.COLOR_SCROLL_INDICATOR,
            border_color=config.COLOR_BORDER,
            bg_color=config.COLOR_WIDGET_BG,
            grid_size=config.GRID_SIZE,
            margin=config.WIDGET_MARGIN,
        )
        self.widgets.append(self.holdings_widget)

        # Total AUM display
        self.aum_widget = TextBoxWidget(
            x=self.width - 90,
            y=self.height - 45,
            width=80,
            height=40,
            total_aum=self.total_aum,
            text_color=config.COLOR_TEXT,
            highlight_color=config.COLOR_TEXT_HIGHLIGHT,
            title="TOTAL AUM",
            border_color=config.COLOR_BORDER,
            bg_color=config.COLOR_WIDGET_BG,
            grid_size=config.GRID_SIZE,
            margin=config.WIDGET_MARGIN,
        )
        self.widgets.append(self.aum_widget)

    def handle_rebalance(self):
        """Handle portfolio rebalancing"""
        print("Rebalancing portfolio...")

    def on_play_pause(self):
        """Toggle play/pause state"""
        self.is_playing = not self.is_playing
        # Update button text
        self.play_button.set_text("Pause" if self.is_playing else "Play")

    def update(self):
        """Update game state (called every frame)"""
        # Update game simulation if playing
        if self.is_playing and pyxel.frame_count % 5 == 0:
            # Advance date by play_speed days
            new_date = self.current_date + datetime.timedelta(days=self.play_speed)
            if new_date <= self.end_date:
                self.current_date = new_date
                # Update timeline widget
                self.timeline_widget.current_date = self.current_date

                # Add a new data point to graph (simulate market movement)
                change = random.uniform(-0.03, 0.03)  # -3% to +3%
                new_aum = self.total_aum * (1 + change)
                self.total_aum = new_aum
                self.aum_widget.total_aum = new_aum

                # Update graph with new value
                normalized_value = new_aum / 1000000 * 100  # Scale to 0-100 range
                self.total_value_line_graph.add_data_point(normalized_value)

        # Update all widgets
        for widget in self.widgets:
            widget.update()

        # Handle widget dragging
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for widget in reversed(self.widgets):  # Check from front to back
                if widget.start_drag(pyxel.mouse_x, pyxel.mouse_y):
                    break  # Only one widget should be dragged at a time

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            for widget in self.widgets:
                widget.update_drag(
                    pyxel.mouse_x, pyxel.mouse_y, self.width, self.height
                )

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            for widget in self.widgets:
                widget.end_drag()

        # G key -> Toggle grid visibility
        if pyxel.btnp(pyxel.KEY_G):
            self.show_grid = not self.show_grid

        # Q or Escape key -> Quit the application
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        """Render the game (called every frame)"""
        pyxel.cls(self.bg_color)  # Clear screen

        if self.show_grid:
            self.draw_grid_dots()

        for widget in self.widgets:
            widget.draw()

    def draw_grid_dots(self):
        """Draw grid dots on the screen"""
        # Draw left and top edges
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                pyxel.pset(x, y, self.grid_color)

        # Draw right edge
        for y in range(0, self.height, self.grid_size):
            pyxel.pset(self.width - 1, y, self.grid_color)

        # Draw bottom edge
        for x in range(0, self.width, self.grid_size):
            pyxel.pset(x, self.height - 1, self.grid_color)

        # Draw bottom right corner
        pyxel.pset(self.width - 1, self.height - 1, self.grid_color)


if __name__ == "__main__":
    App()
