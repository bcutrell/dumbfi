"""
UI layout and widget configuration.

Provides flexible widget positioning and sizing with preset layouts.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class LayoutType(Enum):
    """Predefined layout types."""

    COMPACT = "compact"  # Original 240x180 layout
    STANDARD = "standard"  # Larger 320x240 layout
    WIDE = "wide"  # Wide 400x300 layout
    FULLSCREEN = "fullscreen"  # Full screen layout


@dataclass
class WidgetConfig:
    """Configuration for a single widget."""

    x: int
    y: int
    width: int
    height: int
    draggable: bool = True
    resizeable: bool = False
    visible: bool = True
    z_index: int = 0

    def move_to(self, x: int, y: int) -> "WidgetConfig":
        """Create new config with different position."""
        return WidgetConfig(
            x=x,
            y=y,
            width=self.width,
            height=self.height,
            draggable=self.draggable,
            resizeable=self.resizeable,
            visible=self.visible,
            z_index=self.z_index,
        )

    def resize_to(self, width: int, height: int) -> "WidgetConfig":
        """Create new config with different size."""
        return WidgetConfig(
            x=self.x,
            y=self.y,
            width=width,
            height=height,
            draggable=self.draggable,
            resizeable=self.resizeable,
            visible=self.visible,
            z_index=self.z_index,
        )


@dataclass
class UIConfig:
    """Complete UI layout configuration."""

    layout_type: LayoutType
    screen_width: int
    screen_height: int

    # Widget configurations
    timeline: WidgetConfig
    play_button: WidgetConfig
    rebalance_button: WidgetConfig
    holdings_list: WidgetConfig
    aum_display: WidgetConfig
    portfolio_graph: WidgetConfig

    @classmethod
    def compact_layout(cls) -> "UIConfig":
        """Original compact 240x180 layout."""
        return cls(
            layout_type=LayoutType.COMPACT,
            screen_width=240,
            screen_height=180,
            # Timeline - centered at top
            timeline=WidgetConfig(x=10, y=10, width=220, height=4, resizeable=False),
            # Left column controls
            play_button=WidgetConfig(x=10, y=30, width=60, height=15),
            rebalance_button=WidgetConfig(x=10, y=50, width=60, height=15),
            holdings_list=WidgetConfig(
                x=10, y=70, width=100, height=60, resizeable=True
            ),
            # Right column displays
            aum_display=WidgetConfig(x=170, y=30, width=60, height=35),
            portfolio_graph=WidgetConfig(
                x=150, y=70, width=80, height=60, resizeable=True
            ),
        )

    @classmethod
    def standard_layout(cls) -> "UIConfig":
        """Standard 320x240 layout with more space."""
        return cls(
            layout_type=LayoutType.STANDARD,
            screen_width=320,
            screen_height=240,
            timeline=WidgetConfig(x=20, y=15, width=280, height=6, resizeable=False),
            play_button=WidgetConfig(x=20, y=40, width=80, height=20),
            rebalance_button=WidgetConfig(x=110, y=40, width=80, height=20),
            aum_display=WidgetConfig(x=200, y=40, width=100, height=40),
            holdings_list=WidgetConfig(
                x=20, y=80, width=140, height=140, resizeable=True
            ),
            portfolio_graph=WidgetConfig(
                x=170, y=90, width=130, height=130, resizeable=True
            ),
        )

    @classmethod
    def wide_layout(cls) -> "UIConfig":
        """Wide 400x300 layout for detailed analysis."""
        return cls(
            layout_type=LayoutType.WIDE,
            screen_width=400,
            screen_height=300,
            timeline=WidgetConfig(x=25, y=20, width=350, height=8, resizeable=False),
            play_button=WidgetConfig(x=25, y=45, width=80, height=25),
            rebalance_button=WidgetConfig(x=115, y=45, width=80, height=25),
            aum_display=WidgetConfig(x=280, y=45, width=120, height=50),
            holdings_list=WidgetConfig(
                x=25, y=90, width=180, height=180, resizeable=True
            ),
            portfolio_graph=WidgetConfig(
                x=215, y=105, width=160, height=165, resizeable=True
            ),
        )

    @classmethod
    def from_layout_type(cls, layout_type: LayoutType) -> "UIConfig":
        """Create UI config from layout type."""
        if layout_type == LayoutType.COMPACT:
            return cls.compact_layout()
        elif layout_type == LayoutType.STANDARD:
            return cls.standard_layout()
        elif layout_type == LayoutType.WIDE:
            return cls.wide_layout()
        else:
            raise ValueError(f"Unsupported layout type: {layout_type}")

    def get_widget_config(self, widget_name: str) -> Optional[WidgetConfig]:
        """Get configuration for a specific widget."""
        return getattr(self, widget_name, None)

    def update_widget_config(
        self, widget_name: str, config: WidgetConfig
    ) -> "UIConfig":
        """Create new UI config with updated widget configuration."""
        new_config = UIConfig(
            layout_type=self.layout_type,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            timeline=self.timeline,
            play_button=self.play_button,
            rebalance_button=self.rebalance_button,
            holdings_list=self.holdings_list,
            aum_display=self.aum_display,
            portfolio_graph=self.portfolio_graph,
        )
        setattr(new_config, widget_name, config)
        return new_config

    def scale_layout(self, scale_factor: float) -> "UIConfig":
        """Scale all widget positions and sizes by a factor."""

        def scale_widget(widget: WidgetConfig) -> WidgetConfig:
            return WidgetConfig(
                x=int(widget.x * scale_factor),
                y=int(widget.y * scale_factor),
                width=int(widget.width * scale_factor),
                height=int(widget.height * scale_factor),
                draggable=widget.draggable,
                resizeable=widget.resizeable,
                visible=widget.visible,
                z_index=widget.z_index,
            )

        return UIConfig(
            layout_type=self.layout_type,
            screen_width=int(self.screen_width * scale_factor),
            screen_height=int(self.screen_height * scale_factor),
            timeline=scale_widget(self.timeline),
            play_button=scale_widget(self.play_button),
            rebalance_button=scale_widget(self.rebalance_button),
            holdings_list=scale_widget(self.holdings_list),
            aum_display=scale_widget(self.aum_display),
            portfolio_graph=scale_widget(self.portfolio_graph),
        )

    def get_widget_names(self) -> List[str]:
        """Get list of all widget names."""
        return [
            "timeline",
            "play_button",
            "rebalance_button",
            "holdings_list",
            "aum_display",
            "portfolio_graph",
        ]

    def validate_layout(self) -> List[str]:
        """Validate layout and return any issues."""
        issues = []

        for widget_name in self.get_widget_names():
            widget = self.get_widget_config(widget_name)
            if widget is None:
                continue

            # Check if widget fits in screen
            if widget.x + widget.width > self.screen_width:
                issues.append(f"{widget_name} extends beyond right edge")
            if widget.y + widget.height > self.screen_height:
                issues.append(f"{widget_name} extends beyond bottom edge")
            if widget.x < 0 or widget.y < 0:
                issues.append(f"{widget_name} has negative position")
            if widget.width <= 0 or widget.height <= 0:
                issues.append(f"{widget_name} has invalid dimensions")

        return issues

    def find_widget_overlaps(self) -> List[Tuple[str, str]]:
        """Find overlapping widgets."""
        overlaps = []
        widget_names = self.get_widget_names()

        for i, name1 in enumerate(widget_names):
            widget1 = self.get_widget_config(name1)
            if widget1 is None or not widget1.visible:
                continue

            for name2 in widget_names[i + 1 :]:
                widget2 = self.get_widget_config(name2)
                if widget2 is None or not widget2.visible:
                    continue

                # Check for overlap
                if (
                    widget1.x < widget2.x + widget2.width
                    and widget1.x + widget1.width > widget2.x
                    and widget1.y < widget2.y + widget2.height
                    and widget1.y + widget1.height > widget2.y
                ):
                    overlaps.append((name1, name2))

        return overlaps
