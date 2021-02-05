from finvizfinance.util import scrapFunction, imageScrapFunction
"""
.. module:: crypto
    :synopsis: crypto information

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Crypto:
    """Crypto
    Getting information from the finviz crypto page.

    """
    def __init__(self):
        """initiate module
        """
        pass

    def performance(self):
        """Get crypto performance table.

        Returns:
            df(pandas.DataFrame): crypto performance table
        """
        url = 'https://finviz.com/crypto_performance.ashx'
        df = scrapFunction(url)
        return df

    def chart(self, crypto, timeframe='D', urlonly=False):
        """Get crypto chart.

        Args:
            crypto (str): crypto currency
            timeframe (str): choice of timeframe(5M, H, D, W, M)
            urlonly (bool): choice of downloading charts, default: downloading chart
        Returns:
            charturl(str): url for the chart
        """

        url = 'https://finviz.com/crypto_charts.ashx?t=ALL&tf='
        charturl = imageScrapFunction(url, crypto, timeframe, urlonly)
        return charturl