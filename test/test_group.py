"""Offline fixture tests for the group views (see test_quote for the pattern)."""

import pytest
from conftest import FakeResponse, blocked_response, html_response, use_session

from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError
from finvizfinance.group.custom import Custom
from finvizfinance.group.overview import Overview
from finvizfinance.group.performance import Performance
from finvizfinance.group.spectrum import Spectrum
from finvizfinance.group.util import get_group, get_orders
from finvizfinance.group.valuation import Valuation


def test_group_overview_real():
    use_session(html_response("groups_table.html"))
    df = Overview().screener_view(group="Industry")
    assert list(df["Name"]) == ["Bitcoin", "Ethereum"]


def test_group_drift_raises_parse_error():
    use_session(html_response("groups_table_drift.html"))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(group="Industry")


def test_group_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Overview().screener_view(group="Industry")


def test_group_invalid_group():
    with pytest.raises(ValueError):
        Overview().screener_view(group="Dummy")


def test_group_spectrum_downloads_image(tmp_path, monkeypatch):
    # End-to-end revival check (#advertised-dead-class): before the fix every
    # call died at the order check (``group_order_dict.order_dict``), then at
    # ``request_params.update()`` returning None, then at a positional
    # ``find_all("img")[5]``. Now it fetches the page and downloads the image.
    monkeypatch.chdir(tmp_path)
    fake = use_session(
        [
            html_response("group_spectrum.html"),
            FakeResponse(content=b"\xff\xd8\xff\xe0JPEGBYTES", status_code=200),
        ]
    )
    Spectrum().screener_view(group="Sector", order="Name")
    out = tmp_path / "Sector.jpg"
    assert out.exists()
    assert out.read_bytes() == b"\xff\xd8\xff\xe0JPEGBYTES"
    # Two fetches: the spectrum page, then the spectrum image itself...
    assert len(fake.calls) == 2
    # ...and the image is matched by a stable src pattern, not a fixed index
    # (the fixture holds fewer than 6 <img> and the spectrum is not the 6th).
    assert "spectrum" in fake.calls[1]["url"].lower()


def test_group_spectrum_invalid_group():
    with pytest.raises(ValueError):
        Spectrum().screener_view(group="Dummy")


def test_group_spectrum_invalid_order():
    # The order guard used to read ``group_order_dict.order_dict`` — a plain
    # dict has no such attribute, so *every* call raised AttributeError before
    # it could validate. It must reject a bad order with ValueError now.
    with pytest.raises(ValueError):
        Spectrum().screener_view(order="Dummy")


def test_group_spectrum_missing_image_raises_parse_error():
    use_session(html_response("group_spectrum_missing_image.html"))
    with pytest.raises(FinvizParseError):
        Spectrum().screener_view(group="Sector", order="Name")


def test_group_spectrum_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Spectrum().screener_view(group="Sector", order="Name")


@pytest.mark.parametrize("view_cls", [Overview, Valuation, Performance, Custom])
def test_group_views_parse_groups_table(view_cls):
    # Each group view inherits the shared groups_table parse; exercise them all.
    use_session(html_response("groups_table.html"))
    df = view_cls().screener_view(group="Industry")
    assert list(df["Name"]) == ["Bitcoin", "Ethereum"]


def test_group_custom_parse_columns_sets_c_param():
    view = Custom()
    view._parse_columns([1, 2, 3])
    assert view.request_params["c"] == "1,2,3"


def test_group_custom_parse_columns_empty_is_noop():
    view = Custom()
    view._parse_columns([])
    assert "c" not in view.request_params


def test_group_util_helpers():
    groups = get_group()
    orders = get_orders()
    assert isinstance(groups, list) and "Sector" in groups
    assert isinstance(orders, list) and len(orders) > 0
