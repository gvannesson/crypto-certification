"""Tests des fonctions utilitaires Bloc1_data."""

from datetime import datetime, timezone

import pytest

from src.utils.functions import (
    validate_date,
    parse_date,
    datetime_to_timestamp_ms,
    timestamp_ms_to_datetime,
    round_datetime,
)


class TestValidateDate:
    def test_valid_date_format_ymd(self):
        result = validate_date("2024-06-15")
        assert result == datetime(2024, 6, 15)

    def test_valid_datetime_format(self):
        result = validate_date("2024-06-15 14:30:00")
        assert result == datetime(2024, 6, 15, 14, 30, 0)

    def test_valid_iso_format(self):
        result = validate_date("2024-06-15T14:30:00")
        assert result == datetime(2024, 6, 15, 14, 30, 0)

    def test_invalid_date_returns_none(self):
        assert validate_date("not-a-date") is None

    def test_empty_string_returns_none(self):
        assert validate_date("") is None

    def test_none_input_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            validate_date(None)


class TestParseDate:
    def test_parse_date_ymd(self):
        import pandas as pd
        result = parse_date("2024-01-15")
        assert result == pd.Timestamp("2024-01-15")

    def test_parse_datetime(self):
        import pandas as pd
        result = parse_date("2024-01-15 10:30:00")
        assert result == pd.Timestamp("2024-01-15 10:30:00")

    def test_invalid_returns_nat(self):
        import pandas as pd
        result = parse_date("invalid")
        assert pd.isna(result)


class TestTimestampConversions:
    def test_datetime_to_timestamp_ms(self):
        dt = datetime(2024, 1, 1, 0, 0, 0)
        result = datetime_to_timestamp_ms(dt)
        assert result == 1704067200000

    def test_timestamp_ms_to_datetime(self):
        result = timestamp_ms_to_datetime(1704067200000)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_roundtrip_conversion(self):
        dt = datetime(2024, 6, 15, 12, 30, 0)
        ms = datetime_to_timestamp_ms(dt)
        back = timestamp_ms_to_datetime(ms)
        assert back.year == dt.year
        assert back.month == dt.month
        assert back.day == dt.day
        assert back.hour == dt.hour
        assert back.minute == dt.minute


class TestRoundDatetime:
    def test_round_to_hour(self):
        dt = datetime(2024, 6, 15, 14, 35, 22, 123456)
        result = round_datetime(dt, "hour")
        assert result == datetime(2024, 6, 15, 14, 0, 0, 0)

    def test_round_to_day(self):
        dt = datetime(2024, 6, 15, 14, 35, 22)
        result = round_datetime(dt, "day")
        assert result == datetime(2024, 6, 15, 0, 0, 0, 0)

    def test_unknown_granularity_returns_unchanged(self):
        dt = datetime(2024, 6, 15, 14, 35, 22)
        result = round_datetime(dt, "unknown")
        assert result == dt
