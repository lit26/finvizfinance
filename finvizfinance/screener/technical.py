from finvizfinance.screener.overview import Overview

class Technical(Overview):
    def __init__(self):
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=171{filter}&ft=4'
        self.NUMBER_COL = ['Beta', 'ATR', 'SMA20', 'SMA50', 'SMA200', '52W High',
                           '52W Low', 'RSI', 'Price', 'Change', 'from Open', 'Gap', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()