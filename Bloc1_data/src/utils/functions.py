from datetime import datetime, timezone
from typing import Optional

import pandas as pd


def validate_date(date_str: Optional[str]) -> Optional[datetime]:
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def parse_date(date_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def datetime_to_timestamp_ms(dt: datetime):
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def timestamp_ms_to_datetime(ms: int):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def round_datetime(dt, granularity):
    if granularity == "hour":
        return dt.replace(minute=0, second=0, microsecond=0)
    elif granularity == "day":
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return dt


BINANCE_INTERVAL_MAP = {
    "hour": "1h",
    "day": "1d",
}

BINANCE_SYMBOL_MAP = {
    ("BTC", "USDT"): "BTCUSDT",
    ("BTC", "USD"): "BTCUSD",
    ("Bitcoin", "Tether USDt"): "BTCUSDT",
    ("Bitcoin", "United States Dollar"): "BTCUSD",
}
