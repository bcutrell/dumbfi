from dumbfi.games import TradingSimulator
from dumbfi.config import GameConfig, UIConfig, LayoutType


def main() -> None:
    """Main entry point for DumbFi trading simulator."""
    print("🎮 Starting DumbFi Trading Simulator...")

    # Load configuration - user can customize this
    game_config = GameConfig.load_theme("default")
    ui_config = UIConfig.from_layout_type(LayoutType.STANDARD)

    # Start the trading simulator
    TradingSimulator(game_config, ui_config)
