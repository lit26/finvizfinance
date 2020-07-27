from finvizfinance.util import webScrap, numberCovert
import pandas as pd

class Overview:
    def __init__(self):
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=111{filter}&ft=4'
        self.NUMBER_COL = ['Market Cap', 'P/E', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()

    def _loadfilter(self):
        soup = webScrap(self.url)
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
                        if select != None:
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

    def set_filter(self, filters_dict):
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
        filter_url = ''
        if len(filters) != 0:
            filter_url = '&f=' + ','.join(filters)
        self.url = self.BASE_URL.format(filter=filter_url)

    def _get_page(self,soup):
        options = soup.findAll('table')[17].findAll('option')
        return len(options)

    def _get_table(self, rows, df, num_col_index,table_header):
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

    def ScreenerView(self, verbose=1):
        soup = webScrap(self.url)
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
            print('[Info] loading page {}/{} ...'.format((i+1),page))
            soup = webScrap(self.url+'&r={}'.format(i*20+1))
            table = soup.findAll('table')[18]
            rows = table.findAll('tr')
            df = self._get_table(rows, df, num_col_index, table_header)
        return df


