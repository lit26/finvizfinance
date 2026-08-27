from __future__ import annotations

from finvizfinance.constants import group_dict, group_order_dict


def get_group() -> list[str]:
    """Get groups.

    Returns:
        groups(list): all the available groups.
    """
    return list(group_dict.keys())


def get_orders() -> list[str]:
    """Get orders.

    Returns:
        orders(list): all the available orders.
    """
    return list(group_order_dict.keys())
