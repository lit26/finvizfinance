"""Offline fixture tests for the screener views (see test_quote for the pattern)."""

import json

import pandas as pd
import pytest
from conftest import (
    FakeResponse,
    blocked_response,
    html_response,
    load_fixture,
    use_session,
)

from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError
from finvizfinance.screener import (
    from_url,
    get_filter_options,
    get_filters,
    get_signal,
)
from finvizfinance.screener.custom import Custom
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.util import get_custom_screener_columns, get_orders
from finvizfinance.screener.valuation import Valuation


def test_screener_overview_real():
    use_session(html_response("screener_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]


def test_screener_overview_multipage():
    use_session(
        [
            html_response("screener_multi_p1.html"),
            html_response("screener_multi_p2.html"),
        ]
    )
    df = Overview().screener_view(verbose=0, sleep_sec=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT", "GOOGL"]


def test_screener_custom_default_limit_fetches_all_pages():
    # Custom.screener_view defaults to limit=-1 ("no limit"); the page
    # countdown used to treat it as a number and stop after page one.
    use_session(
        [
            html_response("screener_multi_p1.html"),
            html_response("screener_multi_p2.html"),
        ]
    )
    df = Custom().screener_view(verbose=0, sleep_sec=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT", "GOOGL"]


def test_screener_ticker_not_doubled():
    # Regression (#159): finviz nests two anchors in the ticker cell (a
    # logo/company-ticker link + a tab-link), so the cell's text repeats the
    # symbol ("AAPL" -> "AAPLAAPL"). The parser must read the clean value from
    # the ``data-boxover-ticker`` attribute, without disturbing other columns.
    use_session(html_response("screener_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]
    assert list(df["Company"]) == ["Apple Inc.", "Microsoft"]


def test_screener_duplicate_headers_preserved_across_pages():
    # Regression (#150): a wide custom view can return duplicate header labels
    # (finviz renders two "Dividend" columns). The old name-keyed dict collapsed
    # them, silently shrinking page 1 to a single "Dividend" and then raising
    # ``IndexError`` while parsing page 2, once the cell count exceeded the
    # now-shorter header list.
    use_session(
        [
            html_response("screener_custom_dupcols_p1.html"),
            html_response("screener_custom_dupcols_p2.html"),
        ]
    )
    df = Custom().screener_view(limit=100000, verbose=0, sleep_sec=0)
    # Both "Dividend" columns survive (pandas allows duplicate labels)...
    assert list(df.columns) == ["Ticker", "Dividend", "Sector", "Dividend"]
    # ...all three rows across both pages parsed (no IndexError, no collapse)...
    assert len(df) == 3
    assert list(df.iloc[:, 0]) == ["AAPL", "MSFT", "GOOGL"]
    assert list(df.iloc[:, 2]) == [
        "Technology",
        "Technology",
        "Communication Services",
    ]
    # ...and the two "Dividend" columns hold distinct values (not collapsed).
    assert df.iloc[0, 1] != df.iloc[0, 3]


def test_screener_drift_raises_parse_error():
    use_session(html_response("screener_drift.html"))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_no_results_returns_none():
    use_session(html_response("screener_noresults.html"))
    assert Overview().screener_view(verbose=0) is None


def test_screener_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Overview().screener_view(verbose=0)


def test_screener_ticker_view():
    use_session(html_response("screener_ticker.html"))
    tickers = Ticker().screener_view(verbose=0)
    assert tickers == ["AAPL", "MSFT"]


def test_screener_ticker_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Ticker().screener_view(verbose=0)


def test_screener_ticker_missing_nbsp_no_indexerror():
    # Regression: a ticker cell span without the "<rank>\xa0<TICKER>" NBSP
    # layout made ``text.split("\xa0")[1]`` raise IndexError. The parser must
    # fall back to the span's whole text instead of crashing.
    use_session(html_response("screener_ticker_no_nbsp.html"))
    tickers = Ticker().screener_view(verbose=0)
    assert tickers == ["AAPL", "MSFT"]


# --- redesigned screener (/screener/stocks, Oct 2026) -------------------------
# Results render as a div[role=grid]; paging metadata lives in the
# <script data-ssr-props> JSON island. See issue #187.


def test_screener_ssr_overview():
    use_session(html_response("screener_ssr_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df.columns) == [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ]
    # The ticker cell also holds a logo-tile letter; data-ticker is the clean value.
    assert list(df["Ticker"]) == ["A", "AAPL"]
    assert list(df["Company"]) == ["Agilent Technologies Inc", "Apple Inc"]
    # Cells keep the formatted text, so units match the legacy table parser.
    assert df.loc[0, "Market Cap"] == 48.79e9
    assert df.loc[0, "Change"] == pytest.approx(-0.0047)
    assert df.loc[0, "Volume"] == 1760839


def test_screener_ssr_multipage():
    use_session(
        [
            html_response("screener_ssr_multi_p1.html"),
            html_response("screener_ssr_multi_p2.html"),
        ]
    )
    df = Overview().screener_view(verbose=0, sleep_sec=0)
    assert list(df["Ticker"]) == ["A", "AAPL", "ALB", "ALGN"]
    # A "-" cell still converts to a missing value.
    assert pd.isna(df.loc[2, "P/E"])


def test_screener_ssr_select_page_past_end_returns_none():
    use_session(html_response("screener_ssr_overview.html"))
    assert Overview().screener_view(verbose=0, select_page=2) is None


def test_screener_ssr_legacy_labels():
    # The grid relabels a few columns; they map back to the legacy names.
    use_session(html_response("screener_ssr_valuation.html"))
    df = Valuation().screener_view(verbose=0)
    assert "Fwd P/E" in df.columns and "Forward P/E" not in df.columns
    assert df.loc[0, "Fwd P/E"] == 25.77

    use_session(html_response("screener_ssr_technical.html"))
    df = Technical().screener_view(verbose=0)
    assert {"Change", "Change from Open"} <= set(df.columns)
    assert "Change %" not in df.columns


def test_screener_ssr_no_results_returns_none():
    use_session(html_response("screener_ssr_noresults.html"))
    assert Overview().screener_view(verbose=0) is None


def test_screener_ssr_missing_grid_raises_parse_error():
    use_session(html_response("screener_ssr_drift.html"))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_ssr_bad_island_raises_parse_error():
    use_session(
        FakeResponse(
            text='<script type="application/json" data-ssr-props="x">{"url": "/"}</script>'
        )
    )
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_ssr_ticker_view():
    use_session(html_response("screener_ssr_ticker.html"))
    assert Ticker().screener_view(verbose=0) == ["A", "AAPL", "ABBV"]


def test_screener_ssr_ticker_view_limit():
    use_session(html_response("screener_ssr_ticker.html"))
    assert Ticker().screener_view(verbose=0, limit=2) == ["A", "AAPL"]


def test_screener_ssr_ticker_view_missing_rows_raises_parse_error():
    # totalCount says there are symbols, but the island carries none: Drift.
    html = load_fixture("screener_ssr_ticker.html")
    start, end = html.index('"rows":['), html.index('],"totalCount"')
    use_session(FakeResponse(text=html[:start] + '"rows":[' + html[end:]))
    with pytest.raises(FinvizParseError):
        Ticker().screener_view(verbose=0)


def test_screener_ssr_page_size_mismatch_raises_parse_error():
    # Paging steps by Base.size; a different server page size would skip rows.
    html = load_fixture("screener_ssr_overview.html")
    use_session(FakeResponse(text=html.replace('"pageSize":20', '"pageSize":50')))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_ssr_virtualized_columns_raise_parse_error():
    # A wide view renders only the columns that fit; aria-colcount counts all.
    html = load_fixture("screener_ssr_overview.html")
    use_session(
        FakeResponse(text=html.replace('aria-colcount="11"', 'aria-colcount="40"'))
    )
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_ssr_virtualized_rows_raise_parse_error():
    # The island lists 2 rows; drop one from the grid.
    html = load_fixture("screener_ssr_overview.html")
    use_session(FakeResponse(text=html.replace('data-row-key="AAPL" ', "")))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_ssr_header_without_label_raises_parse_error():
    # Strip the label span from "No." and "Ticker"; the latter must raise.
    html = load_fixture("screener_ssr_overview.html")
    use_session(FakeResponse(text=html.replace("fv-table_header-label", "x", 2)))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_get_settings():
    assert isinstance(get_signal(), list)
    assert isinstance(get_filters(), list)
    assert isinstance(get_filter_options("Exchange"), list)
    with pytest.raises(ValueError):
        get_filter_options("Dummy")


@pytest.mark.parametrize(
    "view_cls", [Financial, Ownership, Performance, Technical, Valuation]
)
def test_screener_views_parse_table(view_cls):
    # Each screener view inherits Base.screener_view; exercise them all.
    use_session(html_response("screener_overview.html"))
    df = view_cls().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]


def test_screener_custom_parse_columns_prepends_zero():
    view = Custom()
    view._parse_columns([2, 1])
    assert view.request_params["c"] == "0,2,1"


def test_screener_custom_parse_columns_dedupes_leading_zero():
    view = Custom()
    view._parse_columns([0, 5])
    assert view.request_params["c"] == "0,5"


def test_screener_custom_parse_columns_empty_is_noop():
    view = Custom()
    view._parse_columns([])
    assert "c" not in view.request_params


def test_screener_util_get_orders_and_columns():
    assert isinstance(get_orders(), list) and len(get_orders()) > 0
    columns = get_custom_screener_columns()
    assert isinstance(columns, dict) and len(columns) > 0


# --- from_url: paste a finviz screener URL instead of building a filters dict ---


def test_from_url_returns_overview_with_filters():
    # The issue #80 example: a finviz screener URL round-trips into the same
    # request params the equivalent set_filter() call would produce.
    url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500,sh_avgvol_o500"
    screener = from_url(url)
    assert isinstance(screener, Overview)
    assert screener.request_params["v"] == 111
    # Filters round-trip exactly (same codes, same order) back to the URL string.
    assert screener.request_params["f"] == "idx_sp500,sh_avgvol_o500"


@pytest.mark.parametrize(
    "v_code, view_cls",
    [
        (111, Overview),
        (121, Valuation),
        (131, Ownership),
        (141, Performance),
        (151, Custom),
        (161, Financial),
        (171, Technical),
        (411, Ticker),
    ],
)
def test_from_url_selects_view_by_v_code(v_code, view_cls):
    screener = from_url(f"https://finviz.com/screener.ashx?v={v_code}&f=idx_sp500")
    assert isinstance(screener, view_cls)
    assert screener.request_params["v"] == v_code


def test_from_url_defaults_to_overview_when_v_absent():
    # finviz serves the Overview view when ``v`` is omitted.
    screener = from_url("https://finviz.com/screener.ashx?f=idx_sp500")
    assert isinstance(screener, Overview)
    assert screener.request_params["v"] == 111


def test_from_url_accepts_bare_query_string():
    screener = from_url("v=121&f=idx_sp500")
    assert isinstance(screener, Valuation)
    assert screener.request_params["f"] == "idx_sp500"


def test_from_url_parses_signal():
    screener = from_url("https://finviz.com/screener.ashx?v=111&s=ta_topgainers")
    assert screener.request_params["s"] == "ta_topgainers"


def test_from_url_parses_ticker():
    screener = from_url("https://finviz.com/screener.ashx?v=411&t=AAPL,MSFT")
    assert isinstance(screener, Ticker)
    assert screener.request_params["t"] == "AAPL,MSFT"


def test_from_url_ignores_order_and_pagination_params():
    # ``o`` (sort) and ``r`` (page offset) are screener_view() concerns, not
    # filter state; from_url ignores them without raising.
    screener = from_url(
        "https://finviz.com/screener.ashx?v=111&f=idx_sp500&o=-marketcap&r=21"
    )
    assert screener.request_params["f"] == "idx_sp500"
    assert "o" not in screener.request_params
    assert "r" not in screener.request_params


def test_from_url_unknown_filter_code_raises():
    # Fail-loud: an unmappable filter code is named and raised, never silently
    # dropped (which would return the wrong stocks).
    with pytest.raises(ValueError, match="totally_bogus"):
        from_url("https://finviz.com/screener.ashx?v=111&f=idx_sp500,totally_bogus")


def test_from_url_unknown_signal_code_raises():
    with pytest.raises(ValueError, match="signal code"):
        from_url("https://finviz.com/screener.ashx?v=111&s=not_a_signal")


def test_from_url_unknown_view_code_raises():
    with pytest.raises(ValueError, match="view code"):
        from_url("https://finviz.com/screener.ashx?v=999&f=idx_sp500")


def test_from_url_non_integer_view_raises():
    with pytest.raises(ValueError, match="Invalid view code"):
        from_url("https://finviz.com/screener.ashx?v=abc")


def test_from_url_no_params_raises():
    with pytest.raises(ValueError, match="No screener parameters"):
        from_url("https://finviz.com/screener.ashx")


def test_from_url_non_string_raises():
    with pytest.raises(TypeError):
        from_url(None)  # type: ignore[arg-type]


def _ssr_grid_page(labels, rows):
    """A minimal redesigned screener page: grid + SSR island.

    ``labels`` excludes "No."; ``rows`` are lists of cell text, ticker first.
    """
    head = "".join(
        f'<div role="columnheader" aria-colindex="{i + 2}">'
        f'<span class="fv-table_header-label">{label}</span></div>'
        for i, label in enumerate(labels)
    )
    body = "".join(
        f'<div role="row" data-row-key="{cells[0]}">'
        + "".join(
            f'<div role="gridcell" aria-colindex="{i + 2}">{text}</div>'
            for i, text in enumerate(cells)
        )
        + "</div>"
        for cells in rows
    )
    island = {
        "data": {
            "rows": [{"text": {"ticker": cells[0]}} for cells in rows],
            "totalCount": len(rows),
            "firstRow": 0,
            "pageSize": 20,
        }
    }
    return FakeResponse(
        text=(
            f'<script type="application/json" data-ssr-props="x">'
            f"{json.dumps(island)}</script>"
            f'<div role="grid" aria-label="Screener results" '
            f'aria-colcount="{len(labels) + 1}">'
            f'<div role="row"><div role="columnheader" data-column-id="row">'
            f'<span class="fv-table_header-label">No.</span></div>{head}</div>'
            f"{body}</div>"
        )
    )


def test_screener_custom_wide_view_is_chunked():
    # The grid virtualizes columns past ~38, so a wide custom view is fetched
    # as narrower chunks (each with Ticker) and joined back on the symbol.
    columns = list(range(1, 61))  # Ticker + 59 others -> chunks of 28, 28, 3
    chunks = [list(range(2, 30)), list(range(30, 58)), list(range(58, 61))]
    tickers = ["AAPL", "MSFT"]
    pages = []
    for n, chunk in enumerate(chunks):
        labels = ["Ticker"] + [f"C{c}" for c in chunk]
        rows = [[t] + [f"{t}-{c}" for c in chunk] for t in tickers]
        if n == 1:
            rows.reverse()  # rows moved between requests: align by ticker
        pages.append(_ssr_grid_page(labels, rows))
    session = use_session(pages)

    view = Custom()
    view.set_filter(filters_dict={"Exchange": "NASDAQ"})
    df = view.screener_view(columns=columns, verbose=0, sleep_sec=0)

    assert list(df.columns) == ["Ticker"] + [f"C{c}" for c in range(2, 61)]
    assert list(df["Ticker"]) == tickers
    assert df.loc[1, "C40"] == "MSFT-40"
    assert df.loc[0, "C60"] == "AAPL-60"
    requested = [call["params"]["c"].split(",") for call in session.calls]
    assert requested == [["0", "1", *map(str, chunk)] for chunk in chunks]
    # Every chunk keeps the caller's filter.
    assert all(call["params"].get("f") for call in session.calls)
    assert columns == list(range(1, 61))  # caller's list untouched


def test_screener_custom_wide_view_without_ticker_drops_it():
    columns = list(range(2, 40))  # 38 non-ticker columns -> chunks of 28, 10
    pages = [
        _ssr_grid_page(
            ["Ticker"] + [f"C{c}" for c in chunk],
            [["AAPL"] + [str(c) for c in chunk]],
        )
        for chunk in (range(2, 30), range(30, 40))
    ]
    use_session(pages)
    df = Custom().screener_view(columns=columns, verbose=0, sleep_sec=0)
    assert list(df.columns) == [f"C{c}" for c in range(2, 40)]
