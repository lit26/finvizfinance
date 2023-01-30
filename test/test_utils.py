import pytest
from finvizfinance.util import get_auth_header
from os import environ

def test_get_auth_header_with_wrong_auth():
    header = get_auth_header(email="some", password="some")
    assert(header is None)

def test_get_auth_header_with_right_auth():
    if (environ.get('fv_user') and environ.get('fv_password')):
      header = get_auth_header(email=environ.get('fv_user'), password=environ.get('fv_password'))
      assert(header is not None)
    else :
        pytest.skip("Finviz Elite test requires 'fv_user' and 'fv_password' env variables properly set")
