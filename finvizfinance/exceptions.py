"""
.. module:: exceptions
   :synopsis: Typed error hierarchy for finvizfinance.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

The hierarchy lets callers catch broadly (``FinvizError``) or narrowly
(``FinvizParseError`` / ``FinvizBlockedError``).

Backward compatibility: each subclass also inherits the built-in exception
types that previously propagated from that code path, so existing downstream
``except`` clauses keep catching after an upgrade:

* A structural break used to surface as ``AttributeError`` (a ``find`` returned
  ``None``) or ``IndexError`` (positional table indexing). ``FinvizParseError``
  subclasses those (plus ``KeyError`` / ``TypeError``).
* A Cloudflare Wall used to surface as ``requests.exceptions.HTTPError`` (from
  ``raise_for_status`` on a 403). ``FinvizBlockedError`` subclasses that.
"""

import requests


class FinvizError(Exception):
    """Base class for every error raised by finvizfinance."""


class FinvizParseError(FinvizError, AttributeError, IndexError, KeyError, TypeError):
    """A Structural break: an expected table or region is absent.

    Raised when finviz markup Drifts and a required element cannot be found.
    Carries the ``url`` and the failed ``selector`` so Drift can be diagnosed.
    """

    def __init__(self, message=None, url=None, selector=None):
        self.url = url
        self.selector = selector
        if message is None:
            message = (
                "Failed to parse finviz response: required element "
                "'{selector}' not found at {url}. "
                "Finviz markup may have changed (Drift)."
            ).format(selector=selector, url=url)
        super().__init__(message)


class FinvizBlockedError(FinvizError, requests.exceptions.HTTPError):
    """A Wall: finviz (Cloudflare) is blocking the request by IP reputation.

    Raised after bounded retries when a request is met with a Cloudflare
    challenge (HTTP 403 "Just a moment") or repeatedly times out. Carries the
    ``url``.
    """

    def __init__(self, message=None, url=None):
        self.url = url
        if message is None:
            message = (
                "finviz blocked the request at {url} (Cloudflare challenge / 403). "
                "The source IP is being rate-limited. Slow down your request rate, "
                "or supply your own session/proxy via "
                "finvizfinance.util.set_session() or set_proxy()."
            ).format(url=url)
        super().__init__(message)
