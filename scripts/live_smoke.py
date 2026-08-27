#!/usr/bin/env python3
"""Scheduled live-smoke check against real finviz — never gates PR CI.

Intent (per the reliability overhaul spec / ticket 11):

* A Wall (``FinvizBlockedError`` / 403) from the CI datacenter IP is EXPECTED
  and is NOT a failure — it tells us nothing about finviz's markup.
* A parse failure on a 200 (``FinvizParseError``) is a Drift — the actionable
  alert that finviz changed its markup. This fails the job.
* An unexpected error also fails the job.

Exit code is non-zero only when a Drift or unexpected error is seen, so this
job can be scheduled nightly without ever reddening PR CI over a Wall.

Usage::

    python scripts/live_smoke.py
"""

import os
import sys
from collections.abc import Callable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from finvizfinance.exceptions import (  # noqa: E402
    FinvizBlockedError,
    FinvizParseError,
)


def _checks() -> list[tuple[str, Callable[[], None]]]:
    """Named callables that each perform one representative live scrape."""

    def quote_fundament() -> None:
        from finvizfinance.quote import finvizfinance

        finvizfinance("AAPL").ticker_fundament()

    def calendar() -> None:
        from finvizfinance.calendar import Calendar

        Calendar().calendar()

    def insider() -> None:
        from finvizfinance.insider import Insider

        Insider().get_insider()

    def news() -> None:
        from finvizfinance.news import News

        News().get_news()

    def screener() -> None:
        from finvizfinance.screener.overview import Overview

        Overview().screener_view(limit=20, verbose=0)

    def group() -> None:
        from finvizfinance.group.overview import Overview

        Overview().screener_view(group="Sector")

    def crypto() -> None:
        from finvizfinance.crypto import Crypto

        Crypto().performance()

    def futures() -> None:
        from finvizfinance.future import Future

        Future().performance()

    return [
        ("quote.ticker_fundament", quote_fundament),
        ("calendar", calendar),
        ("insider", insider),
        ("news", news),
        ("screener.overview", screener),
        ("group.overview", group),
        ("crypto.performance", crypto),
        ("future.performance", futures),
    ]


def main() -> int:
    drift = []
    errors = []
    blocked = []
    ok = []

    for name, check in _checks():
        try:
            check()
            ok.append(name)
            print(f"OK      {name}")
        except FinvizBlockedError:
            blocked.append(name)
            print(f"BLOCKED {name} (Wall — expected from a datacenter IP)")
        except FinvizParseError as err:
            drift.append(name)
            print(f"DRIFT   {name} -> {err}")
        except Exception as err:  # noqa: BLE001
            errors.append(name)
            print(f"ERROR   {name} -> {type(err).__name__}: {err}")

    print(
        f"\nSummary: {len(ok)} ok, {len(blocked)} blocked (expected), {len(drift)} DRIFT, {len(errors)} error"
    )
    if drift:
        print("Drift detected (finviz markup changed): {}".format(", ".join(drift)))
    if errors:
        print("Unexpected errors: {}".format(", ".join(errors)))

    # A Wall never fails the job; a Drift or unexpected error does.
    return 1 if (drift or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
