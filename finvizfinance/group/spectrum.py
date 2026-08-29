"""
.. module:: group.spectrum
   :synopsis: group spectrum image.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from urllib.parse import urljoin

from finvizfinance.constants import group_dict, group_order_dict
from finvizfinance.group.base import Base
from finvizfinance.util import image_scrap, require, validate_choice, web_scrap


class Spectrum(Base):
    """Spectrum
    Getting information from the finviz group spectrum page.
    """

    v_page = 310

    def screener_view(  # type: ignore[override]  # public API intentionally differs from Base
        self, group: str = "Sector", order: str = "Name", out_dir: str = ""
    ) -> None:
        """Download the group spectrum image.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
        """
        validate_choice(group, group_dict, "group")
        validate_choice(order, group_order_dict, "order")

        self.request_params.update(group_dict[group])
        self.request_params["o"] = group_order_dict[order]

        soup = web_scrap(self.url, self.request_params)
        image = None
        for candidate in soup.find_all("img"):
            src = candidate.get("src", "")
            if "spectrum" in src.lower():
                image = candidate
                break
        image = require(image, self.url, "img[src*=spectrum]")
        url = urljoin("https://finviz.com/", image["src"])
        image_scrap(url, group, "")
