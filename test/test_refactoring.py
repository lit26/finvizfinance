"""Test to verify refactoring doesn't break existing functionality"""

import pytest
from finvizfinance.screener import Overview, Valuation, Performance, Financial, Ownership, Technical
from finvizfinance.group import Overview as GOverview, Valuation as GValuation, Performance as GPerformance
from finvizfinance.crypto import Crypto
from finvizfinance.forex import Forex


def test_screener_classes_have_correct_v_page():
    """Test that screener classes have correct v_page values"""
    assert Overview().v_page == 111
    assert Valuation().v_page == 121
    assert Ownership().v_page == 131
    assert Performance().v_page == 141
    assert Financial().v_page == 161
    assert Technical().v_page == 171


def test_group_classes_have_correct_v_page():
    """Test that group classes have correct v_page values"""
    assert GOverview().v_page == 110
    assert GValuation().v_page == 120
    assert GPerformance().v_page == 140


def test_screener_classes_have_base_methods():
    """Test that screener classes have methods from Base"""
    o = Overview()
    assert hasattr(o, 'screener_view')
    assert hasattr(o, 'set_filter')
    assert hasattr(o, 'reset')
    assert hasattr(o, 'compare')


def test_group_classes_have_base_methods():
    """Test that group classes have methods from Base"""
    o = GOverview()
    assert hasattr(o, 'screener_view')


def test_crypto_forex_inherit_from_market_base():
    """Test that Crypto and Forex classes inherit from MarketBase"""
    c = Crypto()
    f = Forex()
    assert hasattr(c, 'chart')
    assert hasattr(c, 'performance')
    assert hasattr(f, 'chart')
    assert hasattr(f, 'performance')


def test_screener_class_names():
    """Test that classes have correct names"""
    assert Overview.__name__ == 'Overview'
    assert Valuation.__name__ == 'Valuation'
    assert Financial.__name__ == 'Financial'


def test_group_class_names():
    """Test that group classes have correct names"""
    assert GOverview.__name__ == 'Overview'
    assert GValuation.__name__ == 'Valuation'
    assert GPerformance.__name__ == 'Performance'
