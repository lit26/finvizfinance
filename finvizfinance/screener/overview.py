from finvizfinance.util import webScrap, numberCovert
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
        self.NUMBER_COL = ['Market Cap', 'P/E', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(signal='', filter='',ticker='')
        self._loadSetting()

    def _loadSetting(self):
        """load all the signals and filters."""
        soup = webScrap(self.url)

        # signal
        select = soup.find(id='signalSelect')
        options = select.findAll('option')[1:]
        key = [i.text for i in options]
        value = [i['value'].split('&')[1].split('=')[1] for i in options]
        self.signal_dict = dict(zip(key, value))

        # filter
        table = soup.find('td', class_='filters-border')
        rows = table.find('table').children
        filter_dict = {}
        for row in rows:
            if len(row) > 1:
                cols = row.findAll('td')
                for i, col in enumerate(cols):
                    span = col.findAll('span')
                    if len(span) > 0:
                        header = span[0].text
                        continue
                    if header != 'After-Hours Close' and header != 'After-Hours Change':
                        select = col.find('select')
                        if select is not None:
                            option_dict = {}
                            prefix = select['data-filter']
                            option_dict['prefix'] = prefix
                            option_dict['option'] = {}
                            options = col.findAll('option')
                            for option in options:
                                if '(Elite only)' not in option.text:
                                    option_dict['option'][option.text] = option['value']
                            filter_dict[header] = option_dict
        self.filter_dict = filter_dict

        # order
        select = soup.find(id='orderSelect')
        options = select.findAll('option')
        key = [i.text for i in options]
        value = [i['value'].split('&')[2] for i in options]
        self.order_dict = dict(zip(key, value))

    def _set_signal(self,signal):
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

    def _set_ticker(self,ticker):
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
        if signal == '' and filters_dict == {} and ticker =='':
            self.url = self.BASE_URL.format(signal='',filter='', ticker='')
        else:
            url_signal = self._set_signal(signal)
            url_filter = self._set_filters(filters_dict)
            url_ticker = self._set_ticker(ticker)
            self.url = self.BASE_URL.format(signal=url_signal,filter=url_filter,ticker=url_ticker)

    def _get_page(self,soup):
        """Check the page number
        """
        options = soup.findAll('table')[17].findAll('option')
        return len(options)

    def _get_table(self, rows, df, num_col_index,table_header):
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        rows = rows[1:]
        for row in rows:
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

    def ScreenerView(self, order='ticker', verbose=1):
        """Get screener table.

        Args:
            order(str): sort the table by the choice of order
            verbose(int): choice of visual the progress. 1 for visualize progress
        Returns:
            tickers(list): get all the tickers as list.
        """
        url = self.url
        if order != 'ticker':
            if order not in self.order_dict:
                raise ValueError()
            url = self.url+'&'+self.order_dict[order]
        soup = webScrap(url)
        page = self._get_page(soup)
        if page == 0:
            print('No ticker found.')
            return None

        if verbose == 1:
            print('[Info] loading page 1/{} ...'.format(page))
        table = soup.findAll('table')[18]
        rows = table.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')][1:]
        num_col_index = [table_header.index(i) for i in table_header if i in self.NUMBER_COL]
        df = pd.DataFrame([], columns=table_header)
        df = self._get_table(rows, df, num_col_index, table_header)

        for i in range(1, page):
            if verbose == 1:
                print('[Info] loading page {}/{} ...'.format((i+1),page))
            if order == 'ticker':
                soup = webScrap(self.url+'&r={}'.format(i*20+1))
            else:
                soup = webScrap(self.url + '&r={}'.format(i * 20 + 1)+'&'+self.order_dict[order])
            table = soup.findAll('table')[18]
            rows = table.findAll('tr')
            df = self._get_table(rows, df, num_col_index, table_header)
        return df