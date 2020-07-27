from finvizfinance.screener.overview import Overview

class Financial(Overview):
    def __init__(self):
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=161{filter}&ft=4'
        self.NUMBER_COL = ['Market Cap', 'Dividend', 'ROA', 'ROE', 'ROI',
                           'Curr R', 'Quick R', 'LTDebt/Eq', 'Debt/Eq', 'Gross M',
                           'Oper M', 'Profit M', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()