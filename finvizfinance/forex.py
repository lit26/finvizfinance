from finvizfinance.util import scrapFunction, imageScrapFunction
"""
.. module:: forex
   :synopsis: forex.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Forex:
    """Forex
    Getting information from the finviz forex page.
    """
    def __init__(self):
        """initiate module
        """
        pass

    def performance(self, change='percent'):
        """Get forex performance table.

        Args:
            change (str): choose an option of change(percent, PIPS)

        Returns:
            df(pandas.DataFrame): forex performance table
        """
        url = None
        if change == 'percent':
            url = 'https://finviz.com/forex_performance.ashx'
        elif change == 'PIPS':
            url = 'https://finviz.com/forex_performance.ashx?v=1&tv=2&o=-perfdaypct'
        else:
            raise ValueError('Options of change: percent(default), PIPS')
        df = scrapFunction(url)
        return df

    def chart(self, forex, timeframe='D', urlonly=False):
        """Get forex chart.

        Args:
            forex (str): foreign exchange name
            timeframe (str): choice of timeframe(5M, H, D, W, M)
            urlonly (bool): choice of downloading charts, default: downloading chart
        Returns:
            charturl(str): url for the chart
        """
        if forex == '':
            return None

        url = 'https://finviz.com/forex_charts.ashx?t=ALL&tf='
        charturl = imageScrapFunction(url, forex, timeframe, urlonly)
        return charturl