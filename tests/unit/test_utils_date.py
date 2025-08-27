"""
Unit tests for DateUtils functionality.
"""

import pytest
import datetime
from dumbfi.utils import DateUtils


class TestDateUtils:
    """Test DateUtils utility functions."""

    def test_parse_date_valid(self):
        """Test parsing valid date strings."""
        date_str = "2024-06-15"
        result = DateUtils.parse_date(date_str)

        assert isinstance(result, datetime.date)
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_parse_date_invalid(self):
        """Test parsing invalid date strings raises ValueError."""
        with pytest.raises(ValueError):
            DateUtils.parse_date("invalid-date")

        with pytest.raises(ValueError):
            DateUtils.parse_date("2024-13-01")  # Invalid month

    def test_format_date(self, sample_dates):
        """Test formatting date objects to strings."""
        date_obj = sample_dates["current_date"]
        result = DateUtils.format_date(date_obj)

        assert result == "2024-06-15"
        assert isinstance(result, str)

    def test_parse_and_format_roundtrip(self):
        """Test that parsing and formatting are inverse operations."""
        original = "2024-03-20"
        parsed = DateUtils.parse_date(original)
        formatted = DateUtils.format_date(parsed)

        assert formatted == original

    def test_advance_date_default(self, sample_dates):
        """Test advancing date by default 1 day."""
        start_date = sample_dates["current_date"]
        result = DateUtils.advance_date(start_date)

        expected = datetime.date(2024, 6, 16)
        assert result == expected

    def test_advance_date_multiple_days(self, sample_dates):
        """Test advancing date by multiple days."""
        start_date = sample_dates["current_date"]
        result = DateUtils.advance_date(start_date, 10)

        expected = datetime.date(2024, 6, 25)
        assert result == expected

    def test_advance_date_negative(self, sample_dates):
        """Test advancing date by negative days (going backwards)."""
        start_date = sample_dates["current_date"]
        result = DateUtils.advance_date(start_date, -5)

        expected = datetime.date(2024, 6, 10)
        assert result == expected

    def test_days_between(self, sample_dates):
        """Test calculating days between two dates."""
        start_date = sample_dates["start_date"]  # 2024-01-01
        end_date = sample_dates["current_date"]  # 2024-06-15

        result = DateUtils.days_between(start_date, end_date)

        # From Jan 1 to Jun 15, 2024 (leap year)
        # Jan: 31, Feb: 29, Mar: 31, Apr: 30, May: 31, Jun: 15
        # Total: 31 + 29 + 31 + 30 + 31 + 15 = 167 days (inclusive)
        assert result == 167

    def test_days_between_same_date(self, sample_dates):
        """Test days between same date should be 1 (inclusive)."""
        date = sample_dates["current_date"]
        result = DateUtils.days_between(date, date)

        assert result == 1

    def test_is_weekend_saturday(self):
        """Test weekend detection for Saturday."""
        saturday = datetime.date(2024, 6, 15)  # Saturday
        assert DateUtils.is_weekend(saturday) is True

    def test_is_weekend_sunday(self):
        """Test weekend detection for Sunday."""
        sunday = datetime.date(2024, 6, 16)  # Sunday
        assert DateUtils.is_weekend(sunday) is True

    def test_is_weekend_weekday(self):
        """Test weekend detection for weekdays."""
        monday = datetime.date(2024, 6, 17)  # Monday
        friday = datetime.date(2024, 6, 21)  # Friday

        assert DateUtils.is_weekend(monday) is False
        assert DateUtils.is_weekend(friday) is False
