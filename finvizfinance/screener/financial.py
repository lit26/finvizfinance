from finvizfinance.screener.overview import Overview
"""
Module:         screen.financial inherit screen.overview 
Description:    Getting information from the finviz screener financial page.
Author:         Tianning Li
"""

class Financial(Overview):
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=161{filter}&ft=4'
        self.NUMBER_COL = ['Market Cap', 'Dividend', 'ROA', 'ROE', 'ROI',
                           'Curr R', 'Quick R', 'LTDebt/Eq', 'Debt/Eq', 'Gross M',
                           'Oper M', 'Profit M', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()