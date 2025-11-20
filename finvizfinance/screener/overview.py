"""
.. module:: screener.overview
   :synopsis: screen overview table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""

from finvizfinance.screener.base import create_screener

Overview = create_screener(
    v_page=111,
    class_name="Overview",
    doc_string="""Overview
    Getting information from the finviz screener overview page.
    """,
)
