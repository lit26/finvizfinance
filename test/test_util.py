import warnings

import pytest
import requests

from finvizfinance import util
from finvizfinance.util import (
    web_scrap,
    web_scrap_json,
    set_proxy,
    require,
    optional,
    warn_missing,
    find_table_by_headers,
    number_convert,
    number_covert,
)
from finvizfinance.exceptions import (
    FinvizError,
    FinvizParseError,
    FinvizBlockedError,
)
from bs4 import BeautifulSoup

from conftest import use_session, html_response, blocked_response, FakeResponse


# --- transport: injectable session seam -------------------------------------


def test_injected_session_is_used():
    fake = use_session(FakeResponse(text="<html><body>ok</body></html>"))
    soup = web_scrap("https://finviz.com/x")
    assert soup.text.strip() == "ok"
    assert fake.calls[0]["url"] == "https://finviz.com/x"


def test_set_proxy_passed_to_session():
    fake = use_session(FakeResponse(text="<html></html>"))
    proxies = {"https": "http://10.0.0.1:1080"}
    set_proxy(proxies)
    web_scrap("https://finviz.com/x")
    assert fake.calls[0]["proxies"] == proxies


def test_wall_raises_blocked_error():
    fake = use_session(blocked_response())
    with pytest.raises(FinvizBlockedError) as exc:
        web_scrap("https://finviz.com/calendar.ashx")
    assert exc.value.url == "https://finviz.com/calendar.ashx"
    msg = str(exc.value).lower()
    assert "rate-limit" in msg and "proxy" in msg
    # bounded retry: MAX_RETRIES + 1 attempts
    assert len(fake.calls) == util.MAX_RETRIES + 1


def test_timeout_retries_then_blocked_error():
    fake = use_session(requests.exceptions.Timeout("slow"))
    with pytest.raises(FinvizBlockedError):
        web_scrap("https://finviz.com/x")
    assert len(fake.calls) == util.MAX_RETRIES + 1


def test_transient_5xx_then_success():
    fake = use_session(
        [FakeResponse(status_code=503), FakeResponse(text="<html>fine</html>")]
    )
    soup = web_scrap("https://finviz.com/x")
    assert "fine" in soup.text
    assert len(fake.calls) == 2


def test_blocked_error_is_backcompat_httperror():
    # Existing downstream `except requests.exceptions.HTTPError` keeps catching.
    use_session(blocked_response())
    with pytest.raises(requests.exceptions.HTTPError):
        web_scrap("https://finviz.com/x")


def test_web_scrap_json():
    use_session(FakeResponse(content=b'{"data": {"a": 1}}'))
    data = web_scrap_json("https://finviz.com/api/statement.ashx")
    assert data == {"data": {"a": 1}}


def test_fetch_returns_response_through_transport():
    fake = use_session(FakeResponse(text="body"))
    response = util.fetch("https://finviz.com/x")
    assert response.text == "body"
    assert fake.calls[0]["url"] == "https://finviz.com/x"


def test_fetch_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        util.fetch("https://finviz.com/x")


# --- error hierarchy back-compat --------------------------------------------


def test_parse_error_hierarchy():
    err = FinvizParseError(url="u", selector="table.x")
    assert isinstance(err, FinvizError)
    assert isinstance(err, AttributeError)  # old crash type
    assert isinstance(err, IndexError)  # old crash type
    assert err.url == "u" and err.selector == "table.x"


# --- guards ------------------------------------------------------------------


def test_require_present_returns_node():
    soup = BeautifulSoup("<div><table></table></div>", "lxml")
    node = require(soup.find("table"), "u", "table")
    assert node is not None


def test_require_missing_raises_parse_error():
    soup = BeautifulSoup("<div></div>", "lxml")
    with pytest.raises(FinvizParseError) as exc:
        require(soup.find("table"), "https://finviz.com/x", "table.snapshot")
    assert exc.value.selector == "table.snapshot"
    assert exc.value.url == "https://finviz.com/x"


def test_optional_present_returns_node():
    soup = BeautifulSoup("<div><span>hi</span></div>", "lxml")
    assert optional(soup.find("span"), "u", "span").text == "hi"


def test_optional_missing_returns_none_and_warns():
    soup = BeautifulSoup("<div></div>", "lxml")
    with pytest.warns(UserWarning):
        result = optional(soup.find("span"), "u", "span")
    assert result is None


def test_warn_missing_emits_warning():
    with pytest.warns(UserWarning):
        warn_missing("https://finviz.com/x", "some.selector")


def test_find_table_by_headers_matches():
    html = """
    <table><tr><th>Foo</th></tr></table>
    <table><tr><th>Ticker</th><th>Owner</th><th>Transaction</th></tr>
           <tr><td>AAPL</td><td>Cook</td><td>Buy</td></tr></table>
    """
    soup = BeautifulSoup(html, "lxml")
    table = find_table_by_headers(
        soup, ["Ticker", "Owner", "Transaction"], "u", "insider table"
    )
    assert table.find_all("tr")[1].find_all("td")[0].text == "AAPL"


def test_find_table_by_headers_missing_raises_parse_error_not_indexerror():
    soup = BeautifulSoup("<table><tr><th>Foo</th></tr></table>", "lxml")
    with pytest.raises(FinvizParseError):
        find_table_by_headers(soup, ["Ticker", "Owner"], "u", "insider table")


# --- number conversion + deprecated alias -----------------------------------


def test_number_convert():
    assert number_convert("1.5%") == 0.015
    assert number_convert("2B") == 2000000000
    assert number_convert("-") is None
    assert number_convert("1,234") == 1234.0


def test_number_covert_is_deprecated_alias():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert number_covert("3M") == 3000000
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
