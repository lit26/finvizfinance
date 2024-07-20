"""
.. module:: group.custom
   :synopsis: group custom table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.group.base import Base


class Custom(Base):
    """Custom
    Getting information from the finviz group custom page.
    """

    v_page = 152

    def _parse_columns(self, columns):
        if not columns:
            return
        columns = [str(i) for i in columns]
        self.request_params["c"] = ",".join(columns)

    def screener_view(
        self, group="Sector", order="Name", columns=[0, 1, 2, 3, 10, 22, 24, 25, 26]
    ):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
            columns(list): columns of your choice. Default index: 0, 1, 2, 3, 10, 22, 24, 25, 26.
        Returns:
            df(pandas.DataFrame): group information table.
        """
        return Base.screener_view(self, group, order, columns)
