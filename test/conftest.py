"""Shared offline test harness for finvizfinance.

Every scraper reaches finviz through the single ``util`` session seam, so tests
inject a fake session that returns saved HTML (a 200 body), a Cloudflare
challenge (a 403), or raises a timeout — without ever touching the network.
"""

import os
import time

import pytest
import requests

from finvizfinance import util

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def pytest_addoption(parser):
    """Add the opt-in switch for the live (real-network) tests."""
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help=(
            "run @pytest.mark.live tests that hit the real finviz site "
            "(also enabled by setting RUN_LIVE=1)"
        ),
    )


def _live_enabled(config):
    """True when the user opted into live tests via flag or env var."""
    if config.getoption("--run-live"):
        return True
    return os.environ.get("RUN_LIVE", "").strip().lower() in {"1", "true", "yes", "on"}


def pytest_collection_modifyitems(config, items):
    """Skip ``@pytest.mark.live`` tests unless explicitly opted in.

    Keeps the default suite (what CI runs via ``pytest test``) fully offline and
    deterministic: live tests show up as skipped rather than firing real
    requests — or failing to collect — when nobody asked for them.
    """
    if _live_enabled(config):
        return
    skip_live = pytest.mark.skip(
        reason="live test: pass --run-live or set RUN_LIVE=1 to run against finviz"
    )
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


def load_fixture(name):
    """Read a committed fixture file as text."""
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as f:
        return f.read()


class FakeResponse:
    """A minimal stand-in for ``requests.Response``."""

    def __init__(self, text="", status_code=200, headers=None, content=None):
        self._text = text
        self.status_code = status_code
        self.headers = headers or {}
        self._content = content

    @property
    def text(self):
        return self._text

    @property
    def content(self):
        if self._content is not None:
            return self._content
        return self._text.encode("utf-8")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{self.status_code} Client Error", response=self
            )


def html_response(name):
    """A 200 response carrying the named HTML fixture."""
    return FakeResponse(text=load_fixture(name), status_code=200)


def blocked_response():
    """A 403 Cloudflare-challenge response (a Wall)."""
    return FakeResponse(
        text=load_fixture("blocked_challenge.html"),
        status_code=403,
        headers={"cf-mitigated": "challenge"},
    )


class FakeSession:
    """Return canned outcomes for successive ``get`` calls.

    ``outcomes`` is a single item or a list consumed in order (the last item
    repeats once the list is exhausted). Each item is either a
    :class:`FakeResponse` to return or an ``Exception`` to raise.
    """

    def __init__(self, outcomes):
        if not isinstance(outcomes, list):
            outcomes = [outcomes]
        self._outcomes = outcomes
        self.calls = []

    def get(
        self,
        url,
        params=None,
        headers=None,
        timeout=None,
        proxies=None,
        stream=False,
    ):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
                "proxies": proxies,
                "stream": stream,
            }
        )
        idx = min(len(self.calls) - 1, len(self._outcomes) - 1)
        outcome = self._outcomes[idx]
        if isinstance(outcome, Exception):
            raise outcome
        if isinstance(outcome, type) and issubclass(outcome, Exception):
            raise outcome()
        return outcome


def use_session(outcomes):
    """Install a :class:`FakeSession` and return it for assertions."""
    fake = FakeSession(outcomes)
    util.set_session(fake)
    return fake


@pytest.fixture(autouse=True)
def _no_sleep_and_restore(request, monkeypatch):
    """Neutralize backoff sleeps and restore the real session after each test.

    Live tests (``@pytest.mark.live``) keep the real ``time.sleep`` so their
    bounded backoff against a genuine Cloudflare Wall stays polite; they still
    get the session and proxy restored afterward.
    """
    if request.node.get_closest_marker("live") is None:
        monkeypatch.setattr(time, "sleep", lambda *a, **k: None)
    original = util.get_session()
    original_proxy = util.proxy_dict
    yield
    util.set_session(original)
    util.set_proxy(original_proxy)
