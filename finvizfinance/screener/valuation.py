from finvizfinance.screener.overview import Overview
"""
Module:         screen.valuation inherit screen.overview 
Description:    Getting information from the finviz screener valuation page.
Author:         Tianning Li
"""

class Valuation(Overview):
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=121{filter}&ft=4'
        self.NUMBER_COL = ['Market Cap', 'P/E', 'Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/C', \
                           'P/FCF', 'EPS this Y', 'EPS next Y', 'EPS past 5Y', 'EPS next 5Y', \
                           'Sales past 5Y', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()