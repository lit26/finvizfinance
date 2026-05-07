import pytest
from bs4 import BeautifulSoup
from finvizfinance.screener import (
    Overview,
    get_signal,
    get_filters,
    get_filter_options
)
from finvizfinance.screener.base import Base


def test_screener_overview():
    foverview = Overview()
    filters_dict = {'Exchange': 'AMEX', 'Sector': 'Basic Materials'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view(order="Company", ascend=False)
    assert(df is not None)
    ticker = 'TSLA'
    foverview.set_filter(signal='', filters_dict={}, ticker=ticker)
    df = foverview.screener_view()
    assert(df is not None)


def test_screener_get_settings():
    signals = get_signal()
    assert type(signals) is list

    filters = get_filters()
    assert type(filters) is list

    filter_options = get_filter_options('Exchange')
    assert type(filter_options) is list

    with pytest.raises(ValueError):
        get_filter_options('Dummy')


def _make_screener_soup(headers, rows_data):
    """Build a minimal BeautifulSoup matching the structure ``Base._parse_table``
    expects: a ``<table class="screener_table">`` whose first ``<tr>`` carries
    the ``<th>`` cells (with a leading row-number header) and whose subsequent
    ``<tr>``s carry the data ``<td>`` cells (also with a leading row-number)."""
    th_html = "".join(f"<th>{h}</th>" for h in (["No."] + list(headers)))
    rows_html = ""
    for row_no, values in enumerate(rows_data, start=1):
        tds = "".join(f"<td>{v}</td>" for v in ([row_no] + list(values)))
        rows_html += f"<tr>{tds}</tr>"
    html = (
        '<html><body>'
        '<table class="screener_table">'
        f'<tr>{th_html}</tr>'
        f'{rows_html}'
        '</table>'
        '</body></html>'
    )
    return BeautifulSoup(html, "lxml")


def test_parse_table_handles_duplicate_column_headers():
    """Regression: Finviz occasionally returns duplicate column header names
    (observed: two ``Dividend`` columns when many custom columns are
    requested). The previous ``_get_table`` keyed each row by header name into
    a dict, which silently collapsed duplicates and shrunk page 1's DataFrame
    width by one. On page 2 the loop indexed ``table_header`` by cell position
    and raised ``IndexError: list index out of range`` once the cell count
    exceeded the now-shorter header list."""
    base = Base()

    # Page 1: a duplicate "Dividend" header (positions 1 and 4). Use header
    # names that are NOT in ``NUMBER_COL`` so the assertions are not tangled
    # with ``number_covert``'s string→float conversion.
    headers = ["Ticker", "Dividend", "Sector", "Industry", "Dividend"]
    page1 = _make_screener_soup(
        headers,
        rows_data=[
            ["AAA", "1.00", "Tech", "Software", "0.5%"],
            ["BBB", "2.00", "Health", "Pharma", "1.0%"],
        ],
    )
    df = base._parse_table(None, page1, limit=-1)
    assert len(df) == 2
    # Both Dividend columns should survive — pandas allows duplicate labels.
    assert list(df.columns) == headers

    # Page 2 must reuse page 1's columns; rows have the same cell count as
    # the header (5). With the old name-keyed dict, page 1 collapsed to 4
    # columns and this call would IndexError on cell index 4.
    page2 = _make_screener_soup(
        headers,
        rows_data=[
            ["CCC", "3.00", "Energy", "Oil", "2.0%"],
        ],
    )
    df = base._parse_table(df, page2, limit=-1)
    assert len(df) == 3
    assert list(df.columns) == headers
    # Spot-check non-numeric cells (Ticker / Sector / Industry are outside
    # ``NUMBER_COL``, so they pass through unmodified).
    assert df.iloc[2, 0] == "CCC"
    assert df.iloc[2, 2] == "Energy"
    assert df.iloc[2, 3] == "Oil"


def test_parse_table_pads_short_rows():
    """Defensive: if a row has fewer ``<td>`` cells than the header, the
    missing trailing columns are filled with ``None`` rather than raising."""
    base = Base()
    headers = ["Ticker", "Sector", "Price"]
    soup = _make_screener_soup(
        headers,
        rows_data=[
            ["AAA", "Tech"],  # missing Price
        ],
    )
    df = base._parse_table(None, soup, limit=-1)
    assert df.iloc[0].tolist() == ["AAA", "Tech", None]


def test_parse_table_truncates_extra_cells():
    """Defensive: if a row has more ``<td>`` cells than the header (e.g. a
    transient Finviz HTML quirk), the surplus cells are dropped rather than
    raising ``IndexError``."""
    base = Base()
    headers = ["Ticker", "Sector"]
    soup = _make_screener_soup(
        headers,
        rows_data=[
            ["AAA", "Tech", "Surprise!"],  # one extra
        ],
    )
    df = base._parse_table(None, soup, limit=-1)
    assert df.iloc[0].tolist() == ["AAA", "Tech"]
