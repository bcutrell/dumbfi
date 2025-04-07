import pyxel
import random
from config import (
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_FPS,
    DEFAULT_GRID_SIZE,
    COLOR_BG,
    COLOR_GRID,
    LINE_GRAPH_WIDTH,
    LINE_GRAPH_HEIGHT,
    LINE_GRAPH_INITIAL_X,
    LINE_GRAPH_INITIAL_Y,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_INITIAL_X,
    BUTTON_INITIAL_Y,
)
from widgets import LineGraphWidget, ButtonWidget


class App:
    def __init__(
        self,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        fps=DEFAULT_FPS,
        grid_size=DEFAULT_GRID_SIZE,
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.grid_size = grid_size
        self.show_grid = True
        self.bg_color = COLOR_BG
        self.grid_color = COLOR_GRID

        pyxel.init(self.width, self.height, title="dumbfi", fps=self.fps)

        self.widgets = []
        self.line_graph_widget = LineGraphWidget(
            LINE_GRAPH_INITIAL_X, LINE_GRAPH_INITIAL_Y, LINE_GRAPH_WIDTH, LINE_GRAPH_HEIGHT
        )
        self.widgets.append(self.line_graph_widget)

        self.rebalance_button = ButtonWidget(
            BUTTON_INITIAL_X,
            BUTTON_INITIAL_Y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Trade",
            self.handle_rebalance,
        )
        self.widgets.append(self.rebalance_button)

        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def handle_rebalance(self):
        print("Rebalancing portfolio...")

    def update(self):
        # Add a new random data point every few frames
        if pyxel.frame_count % 5 == 0:
            self.line_graph_widget.add_data_point(random.randint(0, 100))

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
        pyxel.cls(self.bg_color)  # cls = clear screen

        if self.show_grid:
            self.draw_grid_dots()

        for widget in self.widgets:
            widget.draw()

    def draw_grid_dots(self):
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
