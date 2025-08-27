"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path
import datetime
import tempfile
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dumbfi.config import GameConfig, UIConfig, LayoutType
from dumbfi.finance import Portfolio, MarketData


@pytest.fixture
def sample_dates():
    """Provide sample dates for testing."""
    return {
        "start_date": datetime.date(2024, 1, 1),
        "end_date": datetime.date(2024, 12, 31),
        "current_date": datetime.date(2024, 6, 15),
        "date_str": "2024-06-15",
    }


@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing."""
    portfolio = Portfolio(initial_cash=100000, name="Test Portfolio")

    # Add some positions
    portfolio.add_position("AAPL", 10, 150.0, 1.5)
    portfolio.add_position("MSFT", 5, 300.0, 1.5)

    return portfolio


@pytest.fixture
def default_game_config():
    """Create default game configuration."""
    return GameConfig()


@pytest.fixture
def retro_game_config():
    """Create retro theme game configuration."""
    return GameConfig.load_theme("retro")


@pytest.fixture
def standard_ui_config():
    """Create standard UI configuration."""
    return UIConfig.from_layout_type(LayoutType.STANDARD)


@pytest.fixture
def compact_ui_config():
    """Create compact UI configuration."""
    return UIConfig.from_layout_type(LayoutType.COMPACT)


@pytest.fixture
def sample_tickers():
    """Provide sample ticker list."""
    return ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]


@pytest.fixture
def sample_prices():
    """Provide sample price data."""
    return {
        "AAPL": 150.25,
        "MSFT": 300.50,
        "GOOGL": 2800.75,
        "TSLA": 800.00,
        "AMZN": 3200.25,
    }


@pytest.fixture
def temp_csv_file():
    """Create temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        # Write sample CSV data
        f.write("Date,AAPL,MSFT,GOOGL\n")
        f.write("2024-01-01,150.0,300.0,2800.0\n")
        f.write("2024-01-02,151.0,301.0,2801.0\n")
        f.write("2024-01-03,149.0,299.0,2799.0\n")

        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_market_data(temp_csv_file):
    """Create mock market data for testing."""
    return MarketData(temp_csv_file)


@pytest.fixture
def sample_game_state():
    """Create sample game state."""
    from dumbfi.utils import GameState

    return GameState(
        current_date=datetime.date(2024, 6, 15),
        selected_ticker="AAPL",
        trade_quantity=10,
        current_prices={"AAPL": 150.0, "MSFT": 300.0},
    )
