import pyxel
import datetime
import random
from collections import deque


class Widget:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        grid_size=10,
        border_color=13,
        bg_color=1,
        margin=5,
        resizeable=False,
    ):
        # Widget position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid_size = grid_size

        # Dragging state
        self.draggable = True
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.snap_to_grid = True

        # Styles
        self.border_color = border_color
        self.bg_color = bg_color
        self.margin = margin
        self.visible = True

        # Content area (inside margin)
        self.content_x = self.x + self.margin
        self.content_y = self.y + self.margin
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin

        # Resizing state
        self.resizeable = resizeable
        self.resizing = False
        self.resize_handle_size = 8
        self.min_width = 60
        self.min_height = 40

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
        # Check resize handle first
        if self.resizeable and self.is_on_resize_handle(mouse_x, mouse_y):
            return self.start_resize(mouse_x, mouse_y)

        # Then check for dragging
        if not self.draggable:
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
        if self.resizeable:
            self.draw_resize_handle()

    def is_on_resize_handle(self, point_x, point_y):
        """Check if point is on the resize handle (bottom-right corner)"""
        if not self.resizeable:
            return False

        return (
            self.x + self.width - self.resize_handle_size
            <= point_x
            <= self.x + self.width
            and self.y + self.height - self.resize_handle_size
            <= point_y
            <= self.y + self.height
        )

    def start_resize(self, mouse_x, mouse_y):
        """Start resizing if mouse is on resize handle"""
        if not self.resizeable or not self.visible:
            return False

        if self.is_on_resize_handle(mouse_x, mouse_y):
            self.resizing = True
            return True
        return False

    def update_resize(self, mouse_x, mouse_y):
        """Update the widget size during resizing"""
        if not self.resizing or not self.visible:
            return

        # Calculate new width and height, respecting minimum size
        new_width = max(self.min_width, mouse_x - self.x)
        new_height = max(self.min_height, mouse_y - self.y)

        # Snap to grid if enabled
        if self.snap_to_grid and self.grid_size > 0:
            new_width = round(new_width / self.grid_size) * self.grid_size
            new_height = round(new_height / self.grid_size) * self.grid_size

        # Update dimensions
        self.width = new_width
        self.height = new_height

        # Update content area
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin

    def end_resize(self):
        """End the resize operation"""
        self.resizing = False

    def draw_resize_handle(self):
        """Draw the resize handle if widget is resizeable"""
        if not self.resizeable or not self.visible:
            return

        pyxel.rectb(
            self.x + self.width - self.resize_handle_size,
            self.y + self.height - self.resize_handle_size,
            self.resize_handle_size,
            self.resize_handle_size,
            self.border_color,
        )


class ButtonWidget(Widget):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        callback=None,
        active_color=11,
        hover_color=9,
        inactive_color=5,
        text_color=7,
        padding=3,
        **kwargs,
    ):
        super().__init__(x, y, width, height, **kwargs)

        # Button specific properties
        self.text = text
        self.callback = callback
        self.pressed = False
        self.hovered = False
        self.enabled = True

        # Button specific appearance
        self.active_color = active_color
        self.hover_color = hover_color
        self.inactive_color = inactive_color
        self.text_color = text_color
        self.padding = padding

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
    def __init__(
        self,
        x,
        y,
        width,
        height,
        max_points=100,
        min_value=0,
        max_value=100,
        line_color=11,
        **kwargs,
    ):
        super().__init__(x, y, width, height, **kwargs)

        # Graph data and appearance
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.line_color = line_color

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

    def update_graph_dimensions(self):
        """Update internal graph dimensions based on widget size"""
        self.graph_x = self.margin
        self.graph_y = self.margin
        self.graph_width = self.width - 2 * self.margin
        self.graph_height = self.height - 2 * self.margin

    def update_resize(self, mouse_x, mouse_y):
        """Override to update graph dimensions after resizing"""
        # Call the parent class implementation first
        super().update_resize(mouse_x, mouse_y)

        # Then update graph-specific dimensions
        self.update_graph_dimensions()

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
    def __init__(
        self,
        x,
        y,
        width,
        height,
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 12, 31),
        current_date=None,
        border_color=5,
        completed_color=11,
        remaining_color=1,
        text_color=7,
        **kwargs,
    ):
        super().__init__(x, y, width, height, border_color=border_color, **kwargs)

        self.start_date = start_date
        self.end_date = end_date
        self.current_date = current_date if current_date else start_date
        self.days_in_year = (self.end_date - self.start_date).days + 1

        # Timeline colors
        self.completed_color = completed_color
        self.remaining_color = remaining_color
        self.text_color = text_color

    def draw(self):
        # Calculate progress and position
        progress = (self.current_date - self.start_date).days / (self.days_in_year - 1)
        indicator_x = self.x + int(progress * self.width)
        completed_width = int(progress * self.width)
        remaining_width = self.width - completed_width

        # Draw timeline bar with color change
        # First draw the border
        pyxel.rectb(
            self.x,
            self.y,
            self.width,
            self.height,
            self.border_color,
        )

        # Draw completed portion (green)
        if completed_width > 0:
            pyxel.rect(
                self.x,
                self.y,
                completed_width,
                self.height,
                self.completed_color,
            )

        # Draw remaining portion (gray)
        if remaining_width > 0:
            pyxel.rect(
                self.x + completed_width,
                self.y,
                remaining_width,
                self.height,
                self.remaining_color,
            )

        # Draw position indicator
        pyxel.rect(indicator_x - 2, self.y - 4, 4, 16, 8)

        # Draw month markers
        for month in range(1, 13):
            month_date = datetime.date(2024, month, 1)
            month_progress = (month_date - self.start_date).days / (
                self.days_in_year - 1
            )
            month_x = self.x + int(month_progress * self.width)

            # Draw month marker
            pyxel.line(
                month_x,
                self.y - 4,
                month_x,
                self.y + self.height + 4,
                6,
            )

            # Draw month label (abbreviated)
            month_name = month_date.strftime("%b")
            text_x = month_x - len(month_name) * 2
            pyxel.text(text_x, self.y + self.height + 6, month_name, self.text_color)


class ScrollableListWidget(Widget):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        positions=None,
        text_color=7,
        highlight_color=10,
        scroll_indicator_color=7,
        **kwargs,
    ):
        super().__init__(x, y, width, height, **kwargs)

        # Set colors
        self.text_color = text_color
        self.highlight_color = highlight_color
        self.scroll_indicator_color = scroll_indicator_color

        # Default positions if none provided
        if positions is None:
            positions = [
                ("$", 100),
            ]

        # Calculate percentages
        total_value = sum(value for _, value in positions)
        self.position_percentages = [
            (name, value / total_value * 100) for name, value in positions
        ]

        # Scrolling state
        self.scroll_y = 0
        self.max_scroll = max(0, len(positions) * 10 - (self.content_height - 20))
        self.title = "POSITIONS"

    def update(self):
        # Scroll up/down with arrow keys
        if pyxel.btn(pyxel.KEY_UP):
            self.scroll_y = max(0, self.scroll_y - 2)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.scroll_y = min(self.max_scroll, self.scroll_y + 2)

        # Scroll with mouse wheel when mouse is over widget
        if self.is_point_inside(pyxel.mouse_x, pyxel.mouse_y):
            self.scroll_y = max(
                0, min(self.max_scroll, self.scroll_y - pyxel.mouse_wheel * 5)
            )

    def draw(self):
        super().draw()

        # Draw title
        pyxel.text(self.content_x, self.content_y, self.title, self.text_color)
        pyxel.line(
            self.content_x,
            self.content_y + 10,
            self.content_x + self.content_width - 10,
            self.content_y + 10,
            self.border_color,
        )

        # Draw positions in scrollable area
        content_start_y = self.content_y + 15
        available_height = self.content_height - 20

        for i, (name, percentage) in enumerate(self.position_percentages):
            y_pos = content_start_y + i * 10 - self.scroll_y

            # Only draw visible items
            if content_start_y <= y_pos < content_start_y + available_height:
                pyxel.text(self.content_x, y_pos, f"{name}", self.text_color)
                pyxel.text(
                    self.content_x + 45,
                    y_pos,
                    f"{percentage:.1f}%",
                    self.highlight_color,
                )

        # Draw scrollability indicators if needed
        if self.max_scroll > 0:
            # Show up arrow to indicate scrollability
            if self.scroll_y > 0:
                pyxel.tri(
                    self.x + self.width - 10,
                    self.content_y + 15,
                    self.x + self.width - 15,
                    self.content_y + 20,
                    self.x + self.width - 5,
                    self.content_y + 20,
                    self.scroll_indicator_color,
                )

            # Show down arrow to indicate scrollability
            if self.scroll_y < self.max_scroll:
                pyxel.tri(
                    self.x + self.width - 10,
                    self.content_y + self.content_height - 5,
                    self.x + self.width - 15,
                    self.content_y + self.content_height - 10,
                    self.x + self.width - 5,
                    self.content_y + self.content_height - 10,
                    self.scroll_indicator_color,
                )


class TextBoxWidget(Widget):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        total_aum,
        text_color=7,
        highlight_color=10,
        title="TOTAL AUM",
        **kwargs,
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.total_aum = total_aum
        self.title = title
        self.text_color = text_color
        self.highlight_color = highlight_color

    def update(self):
        pass

    def draw(self):
        super().draw()

        # Draw title
        pyxel.text(self.content_x, self.content_y, self.title, self.text_color)

        # Format AUM with commas
        formatted_aum = "${:,.0f}".format(self.total_aum)

        # Center the AUM text
        aum_x = self.x + (self.width // 2) - (len(formatted_aum) * 2)
        aum_y = self.y + (self.height // 2) + 5

        pyxel.text(aum_x, aum_y, formatted_aum, self.highlight_color)
