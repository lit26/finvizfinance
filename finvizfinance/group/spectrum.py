"""
.. module:: group.spectrum
   :synopsis: group spectrum image.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.group.base import Base
from finvizfinance.util import web_scrap, image_scrap
from finvizfinance.constants import group_dict, group_order_dict


class Spectrum(Base):
    """Spectrum
    Getting information from the finviz group spectrum page.
    """

    v_page = 310

    def screener_view(self, group="Sector", order="Name", out_dir=""):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
        """
        if group not in group_dict:
            group_keys = list(group_dict.keys())
            raise ValueError(
                "Invalid group parameter '{}'. Possible parameter input: {}".format(
                    group, group_keys
                )
            )
        if order not in group_order_dict.order_dict:
            order_keys = list(group_order_dict.keys())
            raise ValueError(
                "Invalid order parameter '{}'. Possible parameter input: {}".format(
                    order, order_keys
                )
            )

        self.request_params = self.request_params.update(group_dict[group])
        self.request_params["o"] = group_order_dict[order]

        soup = web_scrap(self.url, self.request_params)
        url = "https://finviz.com/" + soup.find_all("img")[5]["src"]
        image_scrap(url, group, "")
