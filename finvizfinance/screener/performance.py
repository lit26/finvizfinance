from finvizfinance.screener.overview import Overview

class Performance(Overview):
    def __init__(self):
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=141{filter}&ft=4'
        self.NUMBER_COL = ['Perf Week', 'Perf Month', 'Perf Quart', 'Perf Half',
                           'Perf Year', 'Perf YTD', 'Volatility W', 'Volatility M',
                           'Recom', 'Avg Volume', 'Rel Volume', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()