"""
.. module:: group.spectrum
   :synopsis: group spectrum image.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
from finvizfinance.group.overview import Overview
from finvizfinance.util import web_scrap, image_scrap


class Spectrum(Overview):
    """Spectrum inherit from overview module.
    Getting information from the finviz group spectrum page.
    """

    v_page = 310

    def screener_view(self, group="Sector", order="Name", out_dir=""):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
        """
        if group not in self.group_dict:
            raise ValueError()
        if order not in self.order_dict:
            raise ValueError()
        self.url = (
            self.BASE_URL.format(group=self.group_dict[group], v_page=self.v_page)
            + "&"
            + self.order_dict[order]
        )

        soup = web_scrap(self.url)
        url = "https://finviz.com/" + soup.findAll("img")[5]["src"]
        image_scrap(url, group, "")
