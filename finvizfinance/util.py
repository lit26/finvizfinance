"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import sys
import time
import json
import warnings
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date

from finvizfinance.exceptions import (  # noqa: F401  (re-exported for convenience)
    FinvizError,
    FinvizParseError,
    FinvizBlockedError,
)

# A current browser User-Agent. A trivially-outdated client string (the old
# 2020 Chrome/81) is an easy flag for anti-bot heuristics.
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# The single session every request funnels through. It is both the test seam
# and the user-facing extension hook (inject proxies / rotating IPs).
session = requests.Session()

proxy_dict = None
timeout_value = 10

# Bounded exponential backoff for transient failures and Walls.
MAX_RETRIES = 3
BACKOFF_BASE = 0.5
BACKOFF_CAP = 8.0
# Transient HTTP statuses worth retrying (a Wall/403 is handled separately).
RETRY_STATUS = {429, 500, 502, 503, 504}


def set_proxy(proxies):
    """Set proxies on the shared session's requests.

    Args:
        proxies(dict): requests-style proxies mapping.
    """
    global proxy_dict
    proxy_dict = proxies


def set_timeout(timeout):
    """Set the per-request timeout (seconds)."""
    global timeout_value
    timeout_value = timeout


def set_session(new_session):
    """Inject a custom session.

    Lets high-volume users supply their own ``requests``-compatible session
    (with proxies / rotating IPs) to route around IP-reputation Walls. This
    supersedes and absorbs :func:`set_proxy` — a session's own proxy config is
    honored, and :func:`set_proxy` still layers on top.

    Args:
        new_session: an object exposing ``get(url, params, headers, timeout,
            proxies, stream)`` like :class:`requests.Session`.
    """
    global session
    session = new_session


def get_session():
    """Return the session currently used for requests."""
    return session


def _is_wall(response):
    """Detect a Cloudflare Wall (IP-reputation block).

    Recognizes the "Just a moment" / ``cf-mitigated: challenge`` 403 response.
    """
    if getattr(response, "status_code", None) not in (403, 503, 429):
        return False
    if response.headers.get("cf-mitigated") == "challenge":
        return True
    body = getattr(response, "text", "") or ""
    return (
        "Just a moment" in body
        or "cf-chl" in body
        or "challenge-platform" in body
    )


def _retry_after(response, attempt):
    """Seconds to wait before the next attempt, honoring Retry-After."""
    header = response.headers.get("Retry-After") if response is not None else None
    if header and header.replace(".", "", 1).isdigit():
        return min(float(header), BACKOFF_CAP)
    return min(BACKOFF_BASE * (2 ** attempt), BACKOFF_CAP)


def _request(url, params=None, stream=False):
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
            response = session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout_value,
                proxies=proxy_dict,
                stream=stream,
            )
        except requests.exceptions.Timeout as err:
            if attempt < MAX_RETRIES:
                time.sleep(_retry_after(None, attempt))
                continue
            raise FinvizBlockedError(
                message=(
                    "finviz request to {url} timed out after {n} attempts "
                    "({err}). The source IP may be rate-limited; slow down or "
                    "supply a proxy/session via set_session()/set_proxy().".format(
                        url=url, n=MAX_RETRIES + 1, err=err
                    )
                ),
                url=url,
            )

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
                "HTTP error for URL {}: {}".format(url, err)
            )
        return response

    # Unreachable: the loop either returns or raises. Guard anyway.
    raise FinvizBlockedError(url=url)


def web_scrap(url, params=None):
    """Scrap website.

    Args:
        url(str): website
        params(dict): request parameters
    Returns:
        soup(beautiful soup): website html
    """
    response = _request(url, params=params)
    return BeautifulSoup(response.text, "lxml")


def web_scrap_json(url, params=None):
    """Scrap a finviz JSON endpoint through the resilient transport.

    Args:
        url(str): website
        params(dict): request parameters
    Returns:
        data(dict): parsed JSON body
    """
    response = _request(url, params=params)
    return json.loads(response.content)


def fetch(url, params=None, stream=False):
    """Fetch a URL through the resilient transport, returning the response.

    Public entry point for tooling (e.g. the fixture-refresh script) that needs
    the raw response while still honoring the injected session, proxy, timeout,
    backoff, and Wall detection.
    """
    return _request(url, params=params, stream=stream)


def image_scrap(url, ticker, out_dir):
    """scrap website and download image

    Args:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    response = _request(url, stream=True)
    if len(out_dir) != 0:
        out_dir += "/"
    with open("{}{}.jpg".format(out_dir, ticker), "wb") as f:
        f.write(response.content)


def warn_missing(url, selector):
    """Emit the standard Missing-field warning for an absent optional datum."""
    warnings.warn(
        "Optional element '{}' not found at {}".format(selector, url),
        stacklevel=2,
    )


def require(node, url, selector):
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


def optional(node, url, selector, default=None):
    """Return ``node``, or warn and return ``default`` if it is absent.

    Use for an optional datum whose absence is not an error (e.g. an ETF has no
    Sector/Industry). A Missing field comes back as ``None`` with a warning,
    never an exception.
    """
    if node is None:
        warn_missing(url, selector)
        return default
    return node


def find_table_by_headers(soup, required_headers, url, selector):
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


def scrap_function(url):
    """Scrap forex, crypto information.

    Args:
        url(str): website
    Returns:
        df(pandas.DataFrame): performance table
    """
    soup = web_scrap(url)
    table = require(soup.find("table", class_="groups_table"), url, "table.groups_table")
    rows = table.find_all("tr")
    table_header = [i.text.strip() for i in rows[0].find_all("th")][1:]
    frame = []
    rows = rows[1:]
    num_col_index = [i for i in range(2, len(table_header))]
    for row in rows:
        cols = row.find_all("td")[1:]
        info_dict = {}
        for i, col in enumerate(cols):
            if i not in num_col_index:
                info_dict[table_header[i]] = col.text
            else:
                info_dict[table_header[i]] = number_convert(col.text)
        frame.append(info_dict)
    return pd.DataFrame(frame)


def image_scrap_function(url, chart, timeframe, urlonly):
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
            charturl = "https://finviz.com/" + website
            if not urlonly:
                image_scrap(charturl, name, "")
            return charturl
        else:
            continue


def number_convert(num):
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


def number_covert(num):
    """Deprecated misspelled alias of :func:`number_convert`.

    Kept working for backward compatibility; emits a ``DeprecationWarning``.
    """
    warnings.warn(
        "number_covert is a misspelling and is deprecated; use number_convert.",
        DeprecationWarning,
        stacklevel=2,
    )
    return number_convert(num)


def format_datetime(date_str):
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


def progress_bar(page, total):
    bar_len = 30
    filled_len = int(round(bar_len * page / float(total)))
    bar = "#" * filled_len + "-" * (bar_len - filled_len)
    sys.stdout.write("[Info] loading page [{}] {}/{} \r".format(bar, page, total))
    sys.stdout.flush()
