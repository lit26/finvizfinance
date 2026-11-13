"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import contextvars
import json
import logging
import threading
import time
import warnings
from datetime import date, datetime
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from finvizfinance.exceptions import (  # noqa: F401  (re-exported for convenience)
    FinvizBlockedError,
    FinvizError,
    FinvizParseError,
)

logger = logging.getLogger(__name__)

# A current browser User-Agent. A trivially-outdated client string (the old
# 2020 Chrome/81) is an easy flag for anti-bot heuristics.
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# Request configuration is per-context (thread, or async task within a thread)
# so two callers in one process cannot leak a proxy, timeout or session into
# each other. A module-level global would be shared by the whole process.
_session_var: contextvars.ContextVar[Any] = contextvars.ContextVar(
    "finvizfinance_session", default=None
)
_proxy_var: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "finvizfinance_proxy", default=None
)
_timeout_var: contextvars.ContextVar[float] = contextvars.ContextVar(
    "finvizfinance_timeout", default=10
)

# One real Session per thread. `requests.Session` is not thread-safe, so the
# fallback used when nothing was injected must never be shared across threads.
_fallback = threading.local()

# Bounded exponential backoff for transient failures and Walls.
MAX_RETRIES = 3
BACKOFF_BASE = 0.5
BACKOFF_CAP = 8.0
# Transient HTTP statuses worth retrying (a Wall/403 is handled separately).
RETRY_STATUS = {429, 500, 502, 503, 504}


def set_proxy(proxies: dict | None) -> None:
    """Set proxies on this context's requests.

    Args:
        proxies(dict): requests-style proxies mapping.
    """
    _proxy_var.set(proxies)


def get_proxy() -> dict | None:
    """Return the proxies set for this context."""
    return _proxy_var.get()


def set_timeout(timeout: float) -> None:
    """Set the per-request timeout (seconds) for this context."""
    _timeout_var.set(timeout)


def get_timeout() -> float:
    """Return the per-request timeout set for this context."""
    return _timeout_var.get()


def set_session(new_session: Any) -> None:
    """Inject a custom session for this context.

    Lets high-volume users supply their own ``requests``-compatible session
    (with proxies / rotating IPs) to route around IP-reputation Walls. This
    supersedes and absorbs :func:`set_proxy` — a session's own proxy config is
    honored, and :func:`set_proxy` still layers on top.

    The injection is scoped to the calling thread / async task, so one caller's
    session cannot affect another's.

    Args:
        new_session: an object exposing ``get(url, params, headers, timeout,
            proxies, stream)`` like :class:`requests.Session`.
    """
    _session_var.set(new_session)


def get_session() -> Any:
    """Return the session currently used for requests.

    Falls back to a per-thread :class:`requests.Session` when nothing was
    injected.
    """
    injected = _session_var.get()
    if injected is not None:
        return injected
    per_thread = getattr(_fallback, "session", None)
    if per_thread is None:
        per_thread = requests.Session()
        _fallback.session = per_thread
    return per_thread


def __getattr__(name: str) -> Any:
    """Keep the pre-contextvar module-level reads working.

    ``util.session`` / ``util.proxy_dict`` / ``util.timeout_value`` used to be
    readable attributes. They are per-context now, so they are resolved on
    access instead of being stored once at import time.
    """
    legacy = {
        "session": get_session,
        "proxy_dict": get_proxy,
        "timeout_value": get_timeout,
    }
    try:
        return legacy[name]()
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None


def _is_wall(response: Any) -> bool:
    """Detect a Cloudflare Wall (IP-reputation block).

    Recognizes the "Just a moment" / ``cf-mitigated: challenge`` 403 response.
    """
    if getattr(response, "status_code", None) not in (403, 503, 429):
        return False
    if response.headers.get("cf-mitigated") == "challenge":
        return True
    body = getattr(response, "text", "") or ""
    return "Just a moment" in body or "cf-chl" in body or "challenge-platform" in body


def _retry_after(response: Any, attempt: int) -> float:
    """Seconds to wait before the next attempt, honoring Retry-After."""
    header = response.headers.get("Retry-After") if response is not None else None
    if header and header.replace(".", "", 1).isdigit():
        return min(float(header), BACKOFF_CAP)
    return float(min(BACKOFF_BASE * (2**attempt), BACKOFF_CAP))


def _request(url: str, params: dict | None = None, stream: bool = False) -> Any:
    """Fetch a URL through the shared session with bounded retry.

    Retries transient errors (timeouts, 5xx, and Cloudflare Walls) with bounded
    exponential backoff, then raises :class:`FinvizBlockedError` for a Wall or
    exhausted timeouts. Never hangs indefinitely and never blindly swallows a
    real HTTP error.

    Returns:
        requests.Response: the successful response.
    """
    for attempt in range(MAX_RETRIES + 1):
        response = None
        try:
            response = get_session().get(
                url,
                params=params,
                headers=headers,
                timeout=get_timeout(),
                proxies=get_proxy(),
                stream=stream,
            )
        except requests.exceptions.Timeout as err:
            if attempt < MAX_RETRIES:
                time.sleep(_retry_after(None, attempt))
                continue
            raise FinvizBlockedError(
                message=(
                    f"finviz request to {url} timed out after {MAX_RETRIES + 1} attempts "
                    f"({err}). The source IP may be rate-limited; slow down or "
                    "supply a proxy/session via set_session()/set_proxy()."
                ),
                url=url,
            ) from err

        if _is_wall(response):
            if attempt < MAX_RETRIES:
                time.sleep(_retry_after(response, attempt))
                continue
            raise FinvizBlockedError(url=url)

        if response.status_code in RETRY_STATUS and attempt < MAX_RETRIES:
            time.sleep(_retry_after(response, attempt))
            continue

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise requests.exceptions.HTTPError(
                f"HTTP error for URL {url}: {err}"
            ) from err
        return response

    # Unreachable: the loop either returns or raises. Guard anyway.
    raise FinvizBlockedError(url=url)


def web_scrap(url: str, params: dict | None = None) -> BeautifulSoup:
    """Scrap website.

    Args:
        url(str): website
        params(dict): request parameters
    Returns:
        soup(beautiful soup): website html
    """
    response = _request(url, params=params)
    return BeautifulSoup(response.text, "lxml")


def web_scrap_json(url: str, params: dict | None = None) -> Any:
    """Scrap a finviz JSON endpoint through the resilient transport.

    Args:
        url(str): website
        params(dict): request parameters
    Returns:
        data(dict): parsed JSON body
    """
    response = _request(url, params=params)
    return json.loads(response.content)


def fetch(url: str, params: dict | None = None, stream: bool = False) -> Any:
    """Fetch a URL through the resilient transport, returning the response.

    Public entry point for tooling (e.g. the fixture-refresh script) that needs
    the raw response while still honoring the injected session, proxy, timeout,
    backoff, and Wall detection.
    """
    return _request(url, params=params, stream=stream)


def image_scrap(url: str, ticker: str, out_dir: str) -> None:
    """scrap website and download image

    Args:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    response = _request(url, stream=True)
    if len(out_dir) != 0:
        out_dir += "/"
    with open(f"{out_dir}{ticker}.jpg", "wb") as f:
        f.write(response.content)


def warn_missing(url: str, selector: str) -> None:
    """Emit the standard Missing-field warning for an absent optional datum."""
    warnings.warn(
        f"Optional element '{selector}' not found at {url}",
        stacklevel=2,
    )


def require(node: Any, url: str, selector: str) -> Any:
    """Return ``node``, or raise :class:`FinvizParseError` if it is absent.

    Use for a required region whose absence means finviz Drifted.

    Args:
        node: the result of a bs4 lookup (``None`` when absent).
        url(str): the URL being parsed (for the error message).
        selector(str): a human-readable description of what was looked up.
    """
    if node is None:
        raise FinvizParseError(url=url, selector=selector)
    return node


def optional(node: Any, url: str, selector: str, default: Any = None) -> Any:
    """Return ``node``, or warn and return ``default`` if it is absent.

    Use for an optional datum whose absence is not an error (e.g. an ETF has no
    Sector/Industry). A Missing field comes back as ``None`` with a warning,
    never an exception.
    """
    if node is None:
        warn_missing(url, selector)
        return default
    return node


def validate_choice(value: Any, options: Any, label: str) -> Any:
    """Return ``value`` if it is a valid choice, else raise :class:`ValueError`.

    Centralizes the "invalid parameter" guard duplicated across the screener
    and group modules: it checks membership in ``options`` and, on failure,
    raises a ``ValueError`` naming the offending value and listing the valid
    keys.

    Args:
        value: the user-supplied choice.
        options: the valid choices — a mapping whose keys are valid, or any
            membership-testable container.
        label(str): human-readable noun for the message, e.g. ``"order"``.
    Returns:
        the validated ``value`` (for optional chaining).
    """
    if value not in options:
        valid = list(options)
        raise ValueError(f"Invalid {label} '{value}'. Possible {label}: {valid}")
    return value


def find_table_by_headers(
    soup: Any, required_headers: list[str], url: str, selector: str
) -> Any:
    """Find the table whose header row contains all ``required_headers``.

    Replaces fragile positional table indexing: matches on stable header text
    so the lookup survives finviz reordering tables. Raises
    :class:`FinvizParseError` when no such table exists.

    Args:
        soup(beautiful soup): parsed html to search.
        required_headers(list): header texts that must all be present.
        url(str): the URL being parsed (for the error message).
        selector(str): a human-readable description for the error message.
    Returns:
        the matching table node.
    """
    required = {h.lower() for h in required_headers}
    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if header_row is None:
            continue
        header_cells = header_row.find_all(["th", "td"])
        header_texts = {c.text.strip().lower() for c in header_cells}
        if required.issubset(header_texts):
            return table
    raise FinvizParseError(url=url, selector=selector)


def decode_json_after(text: str, start: int, url: str, selector: str) -> Any:
    """Raw-decode a JSON value embedded in ``text`` starting at ``start``.

    Shared by the calendar and futures parsers to pull the JSON argument out
    of a finviz client-side init script (e.g. ``FinvizInit...([...])``). Raises
    :class:`FinvizParseError` when the slice does not begin with valid JSON (a
    finviz Drift).

    Args:
        text(str): the surrounding text (a script body or prettified HTML).
        start(int): offset in ``text`` at which the JSON value begins.
        url(str): the URL being parsed (for the error message).
        selector(str): a human-readable description for the error message.
    """
    try:
        data, _ = json.JSONDecoder().raw_decode(text[start:].lstrip())
    except (json.JSONDecodeError, TypeError) as err:
        raise FinvizParseError(url=url, selector=selector) from err
    return data


def row_to_dict(
    cols: Any, table_header: list[str], num_col_index: list[int]
) -> dict[str, Any]:
    """Build a header-keyed row dict from a table row's ``<td>`` cells.

    Columns whose index is in ``num_col_index`` are passed through
    :func:`number_convert`; the rest keep their raw text. Shared by the group,
    insider, and quote insider-trader parsers.

    Args:
        cols: the row's ``<td>`` cells.
        table_header(list): column names, indexed positionally against ``cols``.
        num_col_index(list): indices of the numeric columns.
    """
    info: dict[str, Any] = {}
    for i, col in enumerate(cols):
        text = col.text
        info[table_header[i]] = number_convert(text) if i in num_col_index else text
    return info


def scrap_group_table(soup: Any, url: str) -> pd.DataFrame:
    """Parse a finviz ``groups_table`` into a DataFrame (header-keyed columns).

    Args:
        soup(beautiful soup): parsed groups page.
        url(str): the URL being parsed (for the error message).
    Returns:
        df(pandas.DataFrame): group information table.
    """
    table = require(
        soup.find("table", class_="groups_table"), url, "table.groups_table"
    )
    rows = table.find_all("tr")
    table_header = [i.text.strip() for i in rows[0].find_all("th")][1:]
    num_col_index = list(range(2, len(table_header)))
    frame = [
        row_to_dict(row.find_all("td")[1:], table_header, num_col_index)
        for row in rows[1:]
    ]
    return pd.DataFrame(frame)


# Redesigned (Nov 2026) performance pages ship rows as JSON in
# <script id="<page>-perf-init-data">. Map them to the legacy column names.
PERF_PERIODS = {
    "5min": "Perf 5Min",
    "Hour": "Perf Hour",
    "Day": "Perf Day",
    "Week": "Perf Week",
    "Month": "Perf Month",
    "Mtd": "Perf MTD",
    "Quarter": "Perf Quarter",
    "HalfYear": "Perf Half",
    "Ytd": "Perf YTD",
    "Year": "Perf Year",
}


def perf_init_rows(soup: Any, url: str, element_id: str) -> list[dict] | None:
    """Rows of a ``<script id=element_id>`` perf payload; None if absent."""
    tag = soup.find("script", id=element_id)
    if tag is None:
        return None
    try:
        rows = json.loads(tag.string or tag.get_text())["rows"]
    except (ValueError, KeyError, TypeError) as err:
        raise FinvizParseError(url=url, selector=f"script#{element_id} rows") from err
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise FinvizParseError(url=url, selector=f"script#{element_id} rows")
    return rows


def perf_frame(rows: list[dict], name_col: str, pips: bool = False) -> pd.DataFrame:
    """Legacy-shaped perf table: percent as fractions (0.025), or raw pips."""
    frame = []
    for row in rows:
        out = {
            "Ticker": row.get("ticker"),
            name_col: row.get("label"),
            "Price": row.get("last"),
        }
        for key, col in PERF_PERIODS.items():
            value = row.get(f"perf{key}{'Pips' if pips else 'Pct'}")
            out[col] = value if pips or value is None else round(value / 100, 6)
        frame.append(out)
    return pd.DataFrame(frame)


def scrap_function(
    url: str, element_id: str | None = None, name_col: str = "Name", pips: bool = False
) -> pd.DataFrame:
    """Scrap forex, crypto information.

    Args:
        url(str): website
        element_id(str): id of the redesigned page's JSON script, if any.
        name_col(str): column name for the row label in the JSON shape.
        pips(bool): report pips instead of percent change (JSON shape).
    Returns:
        df(pandas.DataFrame): performance table
    """
    soup = web_scrap(url)
    if element_id is not None:
        rows = perf_init_rows(soup, url, element_id)
        if rows is not None:
            return perf_frame(rows, name_col, pips)
    return scrap_group_table(soup, url)


def image_scrap_function(
    url: str, chart: str, timeframe: str, urlonly: bool
) -> str | None:
    """Scrap forex, crypto information.

    Args:
        url(str): website
        chart(str): choice of chart
        timeframe (str): choice of timeframe(5M, H, D, W, M)
        urlonly (boolean):  choice of downloading chart
    """
    if timeframe == "5M":
        url += "m5"
    elif timeframe == "H":
        url += "h1"
    elif timeframe == "D":
        url += "d1"
    elif timeframe == "W":
        url += "w1"
    elif timeframe == "M":
        url += "mo"
    else:
        raise ValueError("Invalid timeframe.")

    soup = web_scrap(url)
    content = require(soup.find("div", class_="container"), url, "div.container")
    imgs = content.find_all("img")
    for img in imgs:
        website = img["src"]
        name = website.split("?")[1].split("&")[0].split(".")[0]
        chart_name = name.split("_")[0]
        if chart.lower() == chart_name:
            charturl: str = "https://finviz.com/" + website
            if not urlonly:
                image_scrap(charturl, name, "")
            return charturl
        else:
            continue
    return None


def number_convert(num: str) -> float | None:
    """Convert number(str) to number(float)

    Args:
        num(str): number as a string
    Return:
        num(float or None): number converted to float or None
    """
    if not num or num == "-":  # Check if the string is empty or is "-"
        return None
    num = num.strip()  # Remove any surrounding whitespace
    if num[-1] == "%":
        return float(num[:-1]) / 100
    elif num[-1] == "B":
        return float(num[:-1]) * 1000000000
    elif num[-1] == "M":
        return float(num[:-1]) * 1000000
    elif num[-1] == "K":
        return float(num[:-1]) * 1000
    else:
        return float(num.replace(",", ""))  # Remove commas and convert to float


def number_covert(num: str) -> float | None:
    """Deprecated misspelled alias of :func:`number_convert`.

    Kept working for backward compatibility; emits a ``DeprecationWarning``.
    """
    warnings.warn(
        "number_covert is a misspelling and is deprecated; use number_convert.",
        DeprecationWarning,
        stacklevel=2,
    )
    return number_convert(num)


def format_datetime(date_str: str) -> datetime:
    if date_str.lower().startswith("today"):
        today = date.today()
        time_str = date_str.split()[1]

        hour, minute = map(int, time_str[:-2].split(":"))
        ampm = time_str[-2:]

        if ampm.lower() == "pm" and hour != 12:
            hour += 12
        return datetime(today.year, today.month, today.day, hour, minute)
    else:
        return datetime.strptime(date_str, "%b-%d-%y %I:%M%p")


def progress_bar(page: int, total: int) -> None:
    logger.info("loading page %d/%d", page, total)
