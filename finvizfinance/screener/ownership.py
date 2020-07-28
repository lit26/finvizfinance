from finvizfinance.screener.overview import Overview
"""
Module:         screen.ownership inherit screen.overview 
Description:    Getting information from the finviz screener ownership page.
Author:         Tianning Li
"""

class Ownership(Overview):
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=131{filter}&ft=4'
        self.NUMBER_COL = ['Market Cap', 'Outstanding', 'Float', 'Insider Own',
                           'Insider Trans', 'Inst Own', 'Inst Trans', 'Float Short',
                           'Short Ratio', 'Avg Volume', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()