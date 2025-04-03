import pyxel
import random
from collections import deque


class GraphWidget:
    def __init__(self, x, y, width, height, max_points=100, min_value=0, max_value=100):
        # Widget position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Graph data and appearance
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.line_color = 11  # Yellow
        self.border_color = 5  # Gray
        self.bg_color = 1  # Dark blue

        # Graph boundaries (with margin inside widget)
        self.margin = 5
        self.graph_x = self.margin
        self.graph_y = self.margin
        self.graph_width = self.width - 2 * self.margin
        self.graph_height = self.height - 2 * self.margin

        # Value range
        self.min_value = min_value
        self.max_value = max_value

        # Initialize with some random data
        for _ in range(self.max_points // 2):
            self.add_data_point(random.randint(self.min_value, self.max_value))

    def add_data_point(self, value):
        self.data_points.append(value)

    def is_point_inside(self, point_x, point_y):
        return (
            self.x <= point_x <= self.x + self.width
            and self.y <= point_y <= self.y + self.height
        )

    def start_drag(self, mouse_x, mouse_y):
        if self.is_point_inside(mouse_x, mouse_y):
            self.dragging = True
            self.drag_offset_x = mouse_x - self.x
            self.drag_offset_y = mouse_y - self.y
            return True
        return False

    def update_drag(self, mouse_x, mouse_y, screen_width, screen_height):
        if self.dragging:
            # Calculate new position
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y

            # Keep widget within screen bounds
            new_x = max(0, min(new_x, screen_width - self.width))
            new_y = max(0, min(new_y, screen_height - self.height))

            self.x = new_x
            self.y = new_y

    def end_drag(self):
        self.dragging = False

    def draw(self):
        # Draw widget background and border
        pyxel.rectb(self.x, self.y, self.width, self.height, self.border_color)
        pyxel.rect(
            self.x + 1, self.y + 1, self.width - 2, self.height - 2, self.bg_color
        )

        # Draw the graph
        if len(self.data_points) > 1:
            # Calculate x step based on number of points
            x_step = self.graph_width / (self.max_points - 1)

            # Draw lines connecting data points
            for i in range(len(self.data_points) - 1):
                # Calculate absolute coordinates
                x1 = self.x + self.graph_x + i * x_step
                y1 = (
                    self.y
                    + self.graph_y
                    + self.graph_height
                    - (self.data_points[i] / self.max_value * self.graph_height)
                )
                x2 = self.x + self.graph_x + (i + 1) * x_step
                y2 = (
                    self.y
                    + self.graph_y
                    + self.graph_height
                    - (self.data_points[i + 1] / self.max_value * self.graph_height)
                )

                # Draw the line segment
                pyxel.line(x1, y1, x2, y2, self.line_color)


class App:
    def __init__(self, width=160, height=120, fps=30, grid_size=20):
        self.width = width
        self.height = height
        self.fps = fps
        self.bg_color = 0  # Black
        self.grid_color = 2  # Dark purple
        self.grid_size = grid_size
        self.show_grid = True

        pyxel.init(self.width, self.height, title="dumbfi", fps=self.fps)

        # Create the graph widget
        graph_width = 60
        graph_height = 20
        initial_x = (self.width - graph_width) // 2
        initial_y = (self.height - graph_height) // 2
        self.graph_widget = GraphWidget(initial_x, initial_y, graph_width, graph_height)

        # Enable mouse input visibility
        pyxel.mouse(True)

        # Start the app
        pyxel.run(self.update, self.draw)

    def update(self):
        # Add a new random data point every few frames
        if pyxel.frame_count % 5 == 0:
            self.graph_widget.add_data_point(random.randint(0, 100))

        # Handle mouse interaction for dragging
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.graph_widget.start_drag(pyxel.mouse_x, pyxel.mouse_y)

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self.graph_widget.update_drag(
                pyxel.mouse_x, pyxel.mouse_y, self.width, self.height
            )

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.graph_widget.end_drag()


        # G key -> Toggle grid visibility
        if pyxel.btnp(pyxel.KEY_G):
            self.show_grid = not self.show_grid

        # Q or Escape key -> Quit the application
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        # Clear the screen
        pyxel.cls(self.bg_color)

        # Draw Grid
        if self.show_grid:
            self.draw_grid()

        # Draw the graph widget
        self.graph_widget.draw()

    def draw_grid(self):
        # Draw dots at grid intersections
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                pyxel.pset(x, y, self.grid_color)

if __name__ == "__main__":
    App(width=240, height=180, fps=30, grid_size=10)
