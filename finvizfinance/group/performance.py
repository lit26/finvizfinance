"""
.. module:: group.performance
   :synopsis: group performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.group.base import create_group

Performance = create_group(
    v_page=140,
    class_name="Performance",
    doc_string="""Performance
    Getting information from the finviz group performance page.
    """,
)
