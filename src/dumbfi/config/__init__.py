"""
Configuration management for DumbFi.

Provides flexible configuration system for games, themes, and settings.
"""

from .game_config import GameConfig, Theme
from .ui_config import UIConfig, WidgetConfig, LayoutType

__all__ = ["GameConfig", "Theme", "UIConfig", "WidgetConfig", "LayoutType"]
