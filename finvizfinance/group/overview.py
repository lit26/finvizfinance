"""
.. module:: group.overview
   :synopsis: group overview table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.group.base import create_group

Overview = create_group(
    v_page=110,
    class_name="Overview",
    doc_string="""Overview
    Getting information from the finviz group overview page.
    """,
)
