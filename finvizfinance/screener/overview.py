from finvizfinance.util import webScrap, numberCovert, progressBar, NUMBER_COL, util_dict
from finvizfinance.quote import finvizfinance
import pandas as pd
"""
.. module:: screen.overview
   :synopsis: screen overview table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""


class Overview:
    """Overview
    Getting information from the finviz screener overview page.
    """
    def __init__(self):
        """initiate module"""
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=111{signal}{filter}&ft=4{ticker}'
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        self._loadSetting()

    def _loadSetting(self):
        """load all the signals and filters."""
        data = util_dict
        self.signal_dict = data['signal']
        self.filter_dict = data['filter']
        self.order_dict = data['order']

    def _set_signal(self, signal):
        """set signal.

        Args:
            signal(str): ticker signal
        Returns:
            url_signal(str): signal string for url
        """
        url_signal = ''
        if signal not in self.signal_dict and signal != '':
            print('No "{}" signal. Please try again.'.format(signal))
            raise ValueError()
        elif signal != '':
            url_signal = '&s=' + self.signal_dict[signal]
        return url_signal

    def getSignal(self):
        """Get signals.

        Returns:
            signals(list): all the available trading signals
        """
        return list(self.signal_dict.keys())

    def getFilters(self):
        """Get filters.

        Returns:
            filters(list): all the available filters
        """
        return list(self.filter_dict.keys())

    def getFilterOptions(self, screen_filter):
        """Get filters options.

        Args:
            screen_filter(str): screen filter for checking options

        Returns:
            filter_options(list): all the available filters
        """
        if screen_filter not in self.filter_dict:
            print('Invalid filter.')
            raise ValueError()
        return list(self.filter_dict[screen_filter]['option'])

    def getOrders(self):
        """Get orders.

        Returns:
            orders(list): all the available orders
        """
        return list(self.order_dict.keys())

    def _set_filters(self, filters_dict):
        """Set filters.

        Args:
            filters_dict(dict): dictionary of filters

        Returns:
            url_filter(str): filter string for url
        """
        filters = []
        for key, value in filters_dict.items():
            if key not in self.filter_dict:
                print('No "{}" filter. Please try again.'.format(key))
                raise ValueError()
            if value not in self.filter_dict[key]['option']:
                print('No "{}" filter options. Please check "{}" filter option.'.format(value, key))
                raise ValueError()
            prefix = self.filter_dict[key]['prefix']
            urlcode = self.filter_dict[key]['option'][value]
            if urlcode != '':
                filters.append('{}_{}'.format(prefix, urlcode))
        url_filter = ''
        if len(filters) != 0:
            url_filter = '&f=' + ','.join(filters)
        return url_filter

    def _set_ticker(self, ticker):
        """Set ticker.

        Args:
            ticker(str): ticker string
        Returns:
            url_ticker(str): ticker string for url
        """
        if ticker == '':
            return ''
        return '&t='+ticker

    def set_filter(self, signal='', filters_dict={}, ticker=''):
        """Update the settings.

        Args:
            signal(str): ticker signal
            filters_dict(dict): dictionary of filters
            ticker(str): ticker string
        """
        if signal == '' and filters_dict == {} and ticker == '':
            self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        else:
            url_signal = self._set_signal(signal)
            url_filter = self._set_filters(filters_dict)
            url_ticker = self._set_ticker(ticker)
            self.url = self.BASE_URL.format(signal=url_signal, filter=url_filter, ticker=url_ticker)

    def _get_page(self, soup):
        """Check the page number
        """
        options = soup.findAll('table')[17].findAll('option')
        return len(options)

    def _get_table(self, rows, df, num_col_index, table_header, limit=-1):
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        rows = rows[1:]
        if limit != -1:
            rows = rows[0:limit]

        for index, row in enumerate(rows):
            cols = row.findAll('td')[1:]
            info_dict = {}
            for i, col in enumerate(cols):
                # check if the col is number
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = numberCovert(col.text)
            df = df.append(info_dict, ignore_index=True)
        return df

    def _screener_helper(self, i, page, rows, df, num_col_index, table_header, limit):
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        if i == page - 1:
            df = self._get_table(rows, df, num_col_index, table_header, limit=((limit - 1) % 20 + 1))
        else:
            df = self._get_table(rows, df, num_col_index, table_header)
        return df

    def ScreenerView(self, order='ticker', limit=-1, verbose=1, ascend=True):
        """Get screener table.

        Args:
            order(str): sort the table by the choice of order.
            limit(int): set the top k rows of the screener.
            verbose(int): choice of visual the progress. 1 for visualize progress.
            ascend(bool): if True, the order is ascending.
        Returns:
            df(pandas.DataFrame): screener information table
        """
        url = self.url
        if order != 'ticker':
            if order not in self.order_dict:
                raise ValueError()
            url = self.url+'&'+self.order_dict[order]
        if not ascend:
            url = url.replace('o=', 'o=-')
        soup = webScrap(url)

        page = self._get_page(soup)
        if page == 0:
            print('No ticker found.')
            return None

        if limit != -1:
            if page > (limit-1)//20+1:
                page = (limit-1)//20+1

        if verbose == 1:
            progressBar(1, page)
        table = soup.findAll('table')[18]
        rows = table.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')][1:]
        num_col_index = [table_header.index(i) for i in table_header if i in NUMBER_COL]
        df = pd.DataFrame([], columns=table_header)
        df = self._screener_helper(0, page, rows, df, num_col_index, table_header, limit)

        for i in range(1, page):
            if verbose == 1:
                progressBar(i+1, page)

            url = self.url
            if order == 'ticker':
                url += '&r={}'.format(i * 20 + 1)
            else:
                url += '&r={}'.format(i * 20 + 1) + '&' + self.order_dict[order]
            if not ascend:
                url = url.replace('o=', 'o=-')
            soup = webScrap(url)
            table = soup.findAll('table')[18]
            rows = table.findAll('tr')
            df = self._screener_helper(i, page, rows, df, num_col_index, table_header, limit)
        return df

    def compare(self, ticker, compare_list, order='ticker', verbose=1):
        """Get screener table of similar property (Sector, Industry, Country)

        Args:
            ticker(str): the ticker to compare
            compare_list(list): choice of compare property (Sector, Industry, Country) or combination.
            order(str): sort the table by the choice of order
            verbose(int): choice of visual the progress. 1 for visualize progress
        Returns:
            df(pandas.DataFrame): screener information table
        """
        check_list = ['Sector', 'Industry', 'Country']
        error_list = [i for i in compare_list if i not in check_list]
        if len(error_list) != 0:
            print('Please check: {}'.format(error_list))
            raise ValueError()

        stock = finvizfinance(ticker)
        stock_fundament = stock.TickerFundament()
        filters_dict = {}
        for compare in compare_list:
            filters_dict[compare] = stock_fundament[compare]

        self.set_filter(filters_dict=filters_dict)
        df = self.ScreenerView(order=order, verbose=verbose)
        return df
