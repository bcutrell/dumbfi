import pyxel

from config import (
    COLOR_BORDER,
    COLOR_WIDGET_BG,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_INACTIVE,
    COLOR_TEXT,
    COLOR_GRAPH_LINE,
    WIDGET_MARGIN,
    WIDGET_PADDING,
    DEFAULT_GRID_SIZE,
)

import random
from collections import deque


class Widget:
    def __init__(self, x, y, width, height):
        # Widget position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid_size = DEFAULT_GRID_SIZE

        # Dragging state
        self.draggable = True
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.snap_to_grid = True

        # Appearance
        self.border_color = COLOR_BORDER
        self.bg_color = COLOR_WIDGET_BG
        self.margin = WIDGET_MARGIN

        # Visibility
        self.visible = True

        # Content area (inside margin)
        self.content_x = self.x + self.margin
        self.content_y = self.y + self.margin
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin

    def is_point_inside(self, point_x, point_y):
        return (
            self.x <= point_x <= self.x + self.width
            and self.y <= point_y <= self.y + self.height
        )

    def update_position(self, new_x, new_y):
        delta_x = new_x - self.x
        delta_y = new_y - self.y

        self.x = new_x
        self.y = new_y
        self.content_x += delta_x
        self.content_y += delta_y

    def start_drag(self, mouse_x, mouse_y):
        if not self.draggable or not self.visible:
            return False

        if self.is_point_inside(mouse_x, mouse_y):
            self.dragging = True
            self.drag_offset_x = mouse_x - self.x
            self.drag_offset_y = mouse_y - self.y
            return True
        return False

    def update_drag(self, mouse_x, mouse_y, screen_width, screen_height):
        if not self.dragging or not self.visible:
            return

        # Calculate new position
        new_x = mouse_x - self.drag_offset_x
        new_y = mouse_y - self.drag_offset_y

        # Keep widget within screen bounds
        new_x = max(0, min(new_x, screen_width - self.width))
        new_y = max(0, min(new_y, screen_height - self.height))

        if self.snap_to_grid and self.grid_size > 0:
            new_x = round(new_x / self.grid_size) * self.grid_size
            new_y = round(new_y / self.grid_size) * self.grid_size

        self.update_position(new_x, new_y)

    def end_drag(self):
        self.dragging = False

    def draw_frame(self):
        if not self.visible:
            return

        # Draw border and background
        pyxel.rectb(self.x, self.y, self.width, self.height, self.border_color)
        pyxel.rect(
            self.x + 1, self.y + 1, self.width - 2, self.height - 2, self.bg_color
        )

    def update(self):
        pass  # To be implemented by subclasses

    def draw(self):
        # Content drawing to be implemented by subclasses
        if not self.visible:
            return
        self.draw_frame()


class ButtonWidget(Widget):
    def __init__(self, x, y, width, height, text, callback=None):
        super().__init__(x, y, width, height)

        # Button specific properties
        self.text = text
        self.callback = callback
        self.pressed = False
        self.hovered = False
        self.enabled = True

        # Button specific appearance
        self.active_color = COLOR_BUTTON_ACTIVE
        self.hover_color = COLOR_BUTTON_HOVER
        self.inactive_color = COLOR_BUTTON_INACTIVE
        self.text_color = COLOR_TEXT
        self.padding = WIDGET_PADDING

        self.draggable = False

    def is_enabled(self):
        return self.enabled

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_text(self, text):
        self.text = text

    def handle_click(self, mouse_x, mouse_y):
        if not self.visible or not self.enabled:
            return False

        if self.is_point_inside(mouse_x, mouse_y):
            self.pressed = True
            if self.callback:
                self.callback()
            return True
        return False

    def update_hover(self, mouse_x, mouse_y):
        if not self.visible or not self.enabled:
            self.hovered = False
            return

        self.hovered = self.is_point_inside(mouse_x, mouse_y)

    def release(self):
        self.pressed = False

    def update(self):
        self.update_hover(pyxel.mouse_x, pyxel.mouse_y)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.handle_click(pyxel.mouse_x, pyxel.mouse_y)
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.release()

    def draw(self):
        if not self.visible:
            return

        if not self.enabled:
            button_color = self.inactive_color
        elif self.pressed:
            button_color = self.active_color
        elif self.hovered:
            button_color = self.hover_color
        else:
            button_color = self.inactive_color

        # Draw button background
        pyxel.rect(self.x, self.y, self.width, self.height, button_color)

        # Draw button border
        pyxel.rectb(self.x, self.y, self.width, self.height, self.border_color)

        # Calculate text position for centering
        text_width = len(self.text) * 4  # Approximate width based on character count
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - 5) // 2  # 5 is approximate text height

        # Draw text
        pyxel.text(text_x, text_y, self.text, self.text_color)


class LineGraphWidget(Widget):
    def __init__(self, x, y, width, height, max_points=100, min_value=0, max_value=100):
        super().__init__(x, y, width, height)

        # Graph data and appearance
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.line_color = COLOR_GRAPH_LINE

        # Graph boundaries (with margin inside widget)
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

    def update(self):
        pass

    def draw(self):
        # Draw border and background
        super().draw()

        # Draw graph
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

class TimelineWidget(Widget):
    pass

class TableWidget(Widget):
    pass

class InputBoxWidget(Widget):
    pass