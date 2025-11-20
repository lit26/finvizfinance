"""
.. module:: market_base
   :synopsis: base class for market data (crypto, forex, future)

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.util import scrap_function, image_scrap_function


class MarketBase:
    """MarketBase
    Base class for market data modules (Crypto, Forex).
    """

    def __init__(self):
        """initiate module"""
        pass

    def chart(self, asset, timeframe="D", urlonly=False, chart_url_template=None):
        """Get market chart.

        Args:
            asset (str): asset name (crypto currency or forex pair)
            timeframe (str): choice of timeframe(5M, H, D, W, M)
            urlonly (bool): choice of downloading charts, default: downloading chart
            chart_url_template (str): URL template for the chart
        Returns:
            charturl(str): url for the chart
        """
        if chart_url_template is None:
            raise ValueError("chart_url_template must be provided")

        url = chart_url_template + "ALL&tf="
        charturl = image_scrap_function(url, asset, timeframe, urlonly)
        return charturl
