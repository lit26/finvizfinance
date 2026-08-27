from __future__ import annotations

from finvizfinance.constants import (
    CUSTOM_SCREENER_COLUMNS,
    filter_dict,
    order_dict,
    signal_dict,
)
from finvizfinance.util import validate_choice


def get_signal() -> list[str]:
    """Get signals.

    Returns:
        signals(list): all the available trading signals
    """
    return list(signal_dict.keys())


def get_filters() -> list[str]:
    """Get filters.

    Returns:
        filters(list): all the available filters
    """
    return list(filter_dict.keys())


def get_filter_options(screen_filter: str) -> list[str]:
    """Get filters options.

    Args:
        screen_filter(str): screen filter for checking options

    Returns:
        filter_options(list): all the available filters
    """
    validate_choice(screen_filter, filter_dict, "filter")
    return list(filter_dict[screen_filter]["option"])


def get_orders() -> list[str]:
    """Get orders.

    Returns:
        orders(list): all the available orders
    """
    return list(order_dict.keys())


def get_custom_screener_columns() -> dict[int, str]:
    """Get information about the columns

    Returns:
        columns(dict): return the index and column name.
    """
    return CUSTOM_SCREENER_COLUMNS
