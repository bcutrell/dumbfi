"""
config.py

Color references:
    pub const DEFAULT_COLORS: [Rgb24; NUM_COLORS as usize] = [
        0x000000, 0x2b335f, 0x7e2072, 0x19959c, 0x8b4852, 0x395c98, 0xa9c1ff, 0xeeeeee, //
        0xd4186c, 0xd38441, 0xe9c35b, 0x70c6a9, 0x7696de, 0xa3a3a3, 0xFF9798, 0xedc7b0,
    ];
    pub const COLOR_BLACK: Color = 0;
    pub const COLOR_NAVY: Color = 1;
    pub const COLOR_PURPLE: Color = 2;
    pub const COLOR_GREEN: Color = 3;
    pub const COLOR_BROWN: Color = 4;
    pub const COLOR_DARK_BLUE: Color = 5;
    pub const COLOR_LIGHT_BLUE: Color = 6;
    pub const COLOR_WHITE: Color = 7;
    pub const COLOR_RED: Color = 8;
    pub const COLOR_ORANGE: Color = 9;
    pub const COLOR_YELLOW: Color = 10;
    pub const COLOR_LIME: Color = 11;
    pub const COLOR_CYAN: Color = 12;
    pub const COLOR_GRAY: Color = 13;
    pub const COLOR_PINK: Color = 14;
    pub const COLOR_PEACH: Color = 15;
"""

#
# General
#
SCREEN = {
    "width": 240,
    "height": 180,
    "fps": 30,
    "grid_size": 10,
    "show_grid": True,
}

COLORS = {
    "background": 0,  # Black
    "grid": 5,  # Dark purple
    "border": 13,  # Light gray
    "text": 7,  # White
    "widget_background": 1,  # Dark blue
    "button_active": 11,  # Yellow
    "button_hover": 9,  # Orange
    "button_inactive": 5,  # Dark purple
    "graph_line": 11,  # Yellow,
}

#
# Widgets
#
TOTAL_VALUE_LINE_GRAPH = {
    "width": 120,
    "height": 80,
    "initial_x": (SCREEN["width"] - 120) // 2,
    "initial_y": (SCREEN["height"] - 80) // 2,
}

REBALANCE_BUTTON = {
    "width": 60,
    "height": 15,
    "initial_x": SCREEN["width"] - 60 - 10,
    "initial_y": 10,
}

WIDGETS = {
    "margin": 5,
    "padding": 3,
    "total_value_line_graph": TOTAL_VALUE_LINE_GRAPH,
    "trade_button": REBALANCE_BUTTON,
}
