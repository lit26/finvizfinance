"""
.. module:: screener.custom
   :synopsis: screen custom table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import Base


class Custom(Base):
    """Custom
    Getting information from the finviz screener custom page.
    """

    v_page = 151

    def _parse_columns(self, columns):
        if not columns:
            return
        if 0 in columns:
            columns.remove(0)
        columns.insert(0, 0)
        columns = [str(i) for i in columns]
        self.request_params["c"] = ",".join(columns)

    def screener_view(
        self,
        order="Ticker",
        limit=-1,
        select_page=None,
        verbose=1,
        ascend=True,
        columns=[0, 1, 2, 3, 4, 5, 6, 7, 65, 66, 67],
        sleep_sec=1,
    ):
        """Get screener table.

        Args:
            order(str): sort the table by the choice of order.
            limit(int): set the top k rows of the screener.
            select_page(int): set the page of the screener.
            verbose(int): choice of visual the progress. 1 for visualize progress.
            ascend(bool): if True, the order is ascending.
            columns(list): columns of your choice. Default index: 0,1,2,3,4,5,6,7,65,66,67.
            sleep_sec(int): sleep seconds for fetching each page.
        Returns:
            df(pandas.DataFrame): screener information table
        """
        return Base.screener_view(
            self, order, limit, select_page, verbose, ascend, columns, sleep_sec
        )
