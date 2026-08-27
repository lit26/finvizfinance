#!/usr/bin/env python3
"""Refresh committed live HTML snapshots from finviz through the transport.

These live snapshots live under ``test/fixtures/live/`` and exist so that when
finviz Drifts, re-running this script and committing produces a readable
``git diff`` of exactly what markup moved. They are intentionally SEPARATE from
the curated minimal fixtures the unit suite asserts against (``test/fixtures``)
so that a refresh never destabilizes deterministic tests.

Requests go through ``finvizfinance.util`` so proxy/session config and the
resilient transport apply. From a datacenter IP finviz will Wall most of these
(a ``FinvizBlockedError``) — that is expected; run from an allowed IP or supply
a session/proxy via ``finvizfinance.util.set_session()`` / ``set_proxy()``.

Usage::

    python scripts/refresh_fixtures.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from finvizfinance import util  # noqa: E402
from finvizfinance.exceptions import FinvizBlockedError  # noqa: E402

LIVE_DIR = os.path.join(os.path.dirname(__file__), "..", "test", "fixtures", "live")

TARGETS = {
    "quote_AAPL.html": "https://finviz.com/quote.ashx?t=AAPL",
    "calendar.html": "https://finviz.com/calendar.ashx",
    "insider.html": "https://finviz.com/insidertrading",
    "news.html": "https://finviz.com/news.ashx",
    "screener_overview.html": "https://finviz.com/screener.ashx?v=111",
    "screener_ticker.html": "https://finviz.com/screener.ashx?v=411",
    "group_overview.html": "https://finviz.com/groups.ashx?v=110",
    "crypto.html": "https://finviz.com/crypto_performance.ashx",
    "forex.html": "https://finviz.com/forex_performance.ashx",
    "futures.html": "https://finviz.com/futures_performance.ashx",
    "statement_AAPL_IA.json": "https://finviz.com/api/statement.ashx?t=AAPL&s=IA",
}


def main():
    os.makedirs(LIVE_DIR, exist_ok=True)
    blocked = 0
    for name, url in TARGETS.items():
        path = os.path.join(LIVE_DIR, name)
        try:
            # Reach finviz through the resilient transport (proxy/session aware).
            response = util.fetch(url)
            with open(path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"saved   {name:<28} <- {url}")
        except FinvizBlockedError:
            blocked += 1
            print(f"BLOCKED {name:<28} (Wall — try an allowed IP / proxy)")
        except Exception as err:  # noqa: BLE001 - report and continue refreshing
            print(f"ERROR   {name:<28} {type(err).__name__}: {err}")
    if blocked:
        print(
            f"\n{blocked} endpoint(s) Walled. Supply a proxy/session and re-run to "
            "refresh those."
        )


if __name__ == "__main__":
    main()
