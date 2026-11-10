from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from finvizfinance.constants import (
    CUSTOM_SCREENER_COLUMNS,
    filter_dict,
    order_dict,
    signal_dict,
)
from finvizfinance.util import validate_choice

if TYPE_CHECKING:
    from finvizfinance.screener.base import Base


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


# --- URL -> screener config (issue #80) ------------------------------------
#
# finviz's own UI hands you a screener URL like
# ``screener.ashx?v=111&f=idx_sp500,sh_avgvol_o500``. The reverse indexes below
# turn that URL back into the filter state finvizfinance models, so a caller can
# paste the URL instead of hand-translating every criterion into a filters dict.

# ``prefix_urlcode`` token -> (filter name, option). Built from the same table
# ``Base._set_filters`` walks forward, so it is an exact inverse. Every
# (prefix, code) token is unique, so the mapping is unambiguous.
_FILTER_TOKEN_INDEX: dict[str, tuple[str, str]] = {
    f"{meta['prefix']}_{code}": (name, option)
    for name, meta in filter_dict.items()
    for option, code in meta["option"].items()
    if code != ""
}

# finviz signal code (URL ``s=``) -> signal name.
_SIGNAL_CODE_INDEX: dict[str, str] = {code: name for name, code in signal_dict.items()}


def _view_classes() -> dict[int, type[Base]]:
    """Map each finviz ``v_page`` view code to its screener subclass.

    Imported lazily to avoid a package import cycle: the subclasses import
    ``screener.base`` and ``screener.__init__`` imports this module.
    """
    from finvizfinance.screener.custom import Custom
    from finvizfinance.screener.financial import Financial
    from finvizfinance.screener.overview import Overview
    from finvizfinance.screener.ownership import Ownership
    from finvizfinance.screener.performance import Performance
    from finvizfinance.screener.technical import Technical
    from finvizfinance.screener.ticker import Ticker
    from finvizfinance.screener.valuation import Valuation

    classes: list[type[Base]] = [
        Overview,
        Valuation,
        Ownership,
        Performance,
        Custom,
        Financial,
        Technical,
        Ticker,
    ]
    mapping: dict[int, type[Base]] = {}
    for cls in classes:
        v = cls.v_page
        if v is None:  # pragma: no cover - every screener subclass sets v_page
            continue
        mapping[v] = cls
    return mapping


def from_url(url: str) -> Base:
    """Build a screener from a finviz screener URL (issue #80).

    Reconstructs the *filter state* — view, filters, signal and ticker — from a
    finviz ``screener.ashx`` URL (the link finviz puts in your address bar as you
    click filters in its UI) and returns the matching screener subclass with that
    state already applied. Call :meth:`screener_view` on the result as usual::

        from finvizfinance import screener

        overview = screener.from_url(
            "https://finviz.com/screener.ashx?v=111&f=idx_sp500,sh_avgvol_o500"
        )
        df = overview.screener_view()

    Only the selection parameters are interpreted: ``v`` (view -> subclass),
    ``f`` (filters), ``s`` (signal) and ``t`` (ticker). Sort order (``o``),
    pagination (``r``) and custom columns (``c``) are runtime concerns passed to
    ``screener_view`` and are ignored here.

    Fail-loud: an unknown view code, or any filter/signal code that does not map
    to a known option, raises :class:`ValueError` naming the offending code rather
    than silently dropping it and returning the wrong stocks.

    Args:
        url(str): a finviz screener URL, e.g.
            ``"https://finviz.com/screener.ashx?v=121&f=idx_sp500,sec_technology"``.
            A bare query string (``"v=121&f=idx_sp500"``) is also accepted.

    Returns:
        Base: the screener subclass for the URL's view, with filters/signal/ticker
        applied.
    """
    if not isinstance(url, str):
        raise TypeError(f"url must be a string, got {type(url).__name__}")

    parsed = urlparse(url)
    query = parsed.query
    if not query and "=" in url:
        # Accept a bare query string that has no scheme/host ("v=111&f=...").
        query = url.split("?", 1)[-1]
    params = parse_qs(query)
    if not params:
        raise ValueError(f"No screener parameters (v/f/s/t) found in URL: {url!r}")

    view_classes = _view_classes()
    if "v" in params:
        raw_view = params["v"][0]
        try:
            v_page = int(raw_view)
        except ValueError:
            raise ValueError(
                f"Invalid view code {raw_view!r}. "
                f"Possible view codes: {list(view_classes)}"
            ) from None
        validate_choice(v_page, view_classes, "view code")
        screener_cls = view_classes[v_page]
    else:
        # finviz defaults to the Overview view (v=111) when ``v`` is omitted.
        screener_cls = view_classes[111]

    filters_dict: dict[str, str] = {}
    if "f" in params:
        tokens = [token for value in params["f"] for token in value.split(",") if token]
        unknown = [token for token in tokens if token not in _FILTER_TOKEN_INDEX]
        if unknown:
            raise ValueError(
                f"Unrecognized screener filter code(s) {unknown} in URL. finviz "
                "may have added filters not yet supported by finvizfinance, or "
                "the URL is malformed."
            )
        for token in tokens:
            name, option = _FILTER_TOKEN_INDEX[token]
            filters_dict[name] = option

    signal = ""
    if "s" in params:
        code = params["s"][0]
        if code not in _SIGNAL_CODE_INDEX:
            raise ValueError(
                f"Unrecognized screener signal code {code!r} in URL. "
                f"Possible signal codes: {list(_SIGNAL_CODE_INDEX)}"
            )
        signal = _SIGNAL_CODE_INDEX[code]

    ticker = ",".join(params["t"]) if "t" in params else ""

    screener = screener_cls()
    screener.set_filter(signal=signal, filters_dict=filters_dict, ticker=ticker)
    return screener
