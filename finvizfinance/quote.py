from datetime import datetime
import requests
import json
import pandas as pd
from finvizfinance.util import webScrap, imageScrap, numberCovert, headers
"""
.. module:: finvizfinance
   :synopsis: individual ticker.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
QUOTE_URL = 'https://finviz.com/quote.ashx?t={ticker}'


class Quote:
    """quote
    Getting current price of the ticker

    """
    def getCurrent(self, ticker):
        """Getting current price of the ticker.

        Returns:
            price(float): price of the ticker
        """
        soup = webScrap("https://finviz.com/request_quote.ashx?t={}".format(ticker))
        return soup.text


class finvizfinance:
    """finvizfinance
    Getting information from the individual ticker.

    Args:
        ticker(str): ticker string
        verbose(int): choice of visual the progress. 1 for visualize progress.
    """
    def __init__(self, ticker, verbose=0):
        """initiate module
        """
        self.ticker = ticker
        self.flag = False
        self.quote_url = QUOTE_URL.format(ticker=ticker)
        self.soup = webScrap(self.quote_url)
        if self._checkexist(verbose):
            self.flag = True
        self.info = {}

    def _checkexist(self, verbose):
        try:
            if 'not found' in self.soup.find('td', class_='body-text').text:
                print('Ticker not found.')
                return False
        except:
            if verbose == 1:
                print('Ticker exists.')
            return True

    def TickerCharts(self, timeframe='daily', charttype='advanced', out_dir='', urlonly=False):
        """Download ticker charts.

        Args:
            timeframe(str): choice of timeframe (daily, weekly, monthly).
            charttype(str): choice of type of chart (candle, line, advanced).
            out_dir(str): output image directory. default none.
            urlonly (bool): choice of downloading charts, default: downloading chart

        Returns:
            charturl(str): url for the chart
        """
        if timeframe not in ['daily', 'weekly', 'monthly']:
            raise ValueError()
        if charttype not in ['candle', 'line', 'advanced']:
            raise ValueError()
        url_type = 'c'
        url_ta = '0'
        if charttype == 'line':
            url_type = 'l'
        elif charttype == 'advanced' and timeframe != 'weekly' and timeframe != 'monthly':
            url_ta = '1'

        url_timeframe = 'd'
        if timeframe == 'weekly':
            url_timeframe = 'w'
        elif timeframe == 'monthly':
            url_timeframe = 'm'
        chart_url = 'https://finviz.com/chart.ashx?t={ticker}&ty={type}&ta={ta}&p={timeframe}'.format(ticker=self.ticker,
                                                    type=url_type, ta=url_ta, timeframe=url_timeframe)
        if not urlonly:
            imageScrap(chart_url, self.ticker, out_dir)
        return chart_url

    def TickerFundament(self):
        """Get ticker fundament.

        Returns:
            fundament(dict): ticker fundament.
        """
        fundament_info = {}

        table = self.soup.findAll('table')[5]
        rows = table.findAll('tr')

        fundament_info['Company'] = rows[1].text
        fundament_info['Sector'], fundament_info['Industry'], fundament_info['Country'] = rows[2].text.split(' | ')

        fundament_table = self.soup.find('table', class_='snapshot-table2')
        rows = fundament_table.findAll('tr')

        for row in rows:
            cols = row.findAll('td')
            cols = [i.text for i in cols]
            header = ''
            for i, value in enumerate(cols):
                if i % 2 == 0:
                    header = value
                else:
                    fundament_info[header] = value
        self.info['fundament'] = fundament_info
        return fundament_info

    def TickerDescription(self):
        """Get ticker description.

        Returns:
            description(str): ticker description.
        """
        return self.soup.find('td', class_='fullview-profile').text

    def TickerOuterRatings(self):
        """Get outer ratings table.

        Returns:
            df(pandas.DataFrame): outer ratings table
        """
        fullview_ratings_outer = self.soup.find('table', class_="fullview-ratings-outer")
        df = pd.DataFrame([], columns=['Date', 'Status', 'Outer', 'Rating', 'Price'])
        rows = fullview_ratings_outer.findAll('td', class_="fullview-ratings-inner")
        for row in rows:
            each_row = row.find('tr')
            cols = each_row.findAll('td')
            date = cols[0].text
            date = datetime.strptime(date, '%b-%d-%y')
            status = cols[1].text
            outer = cols[2].text
            rating = cols[3].text
            price = cols[4].text
            df = df.append({'Date': date, 'Status': status, 'Outer': outer, 'Rating': rating, 'Price': price},
                           ignore_index=True)
        self.info['ratings_outer'] = df
        return df

    def TickerNews(self):
        """Get news information table.

        Returns:
            df(pandas.DataFrame): news information table
        """
        fullview_news_outer = self.soup.find('table', class_='fullview-news-outer')
        rows = fullview_news_outer.findAll('tr')

        last_date = ''
        df = pd.DataFrame([], columns=['Date', 'Title', 'Link'])
        for row in rows:
            cols = row.findAll('td')
            date = cols[0].text
            title = cols[1].a.text
            link = cols[1].a['href']
            newsTime = date.split()
            if len(newsTime) == 2:
                last_date = newsTime[0]
                newsTime = ' '.join(newsTime)
            else:
                newsTime = last_date + ' ' + newsTime[0]
            newsTime = datetime.strptime(newsTime, '%b-%d-%y %I:%M%p')
            df = df.append({'Date': newsTime, 'Title': title, 'Link': link}, ignore_index=True)
        self.info['news'] = df
        return df

    def TickerInsideTrader(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        inside_trader = self.soup.find('table', class_='body-table')
        rows = inside_trader.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')]
        table_header += ['Insider_id']
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        num_col = ['Cost', '#Shares', 'Value ($)', '#Shares Total']
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.findAll('td')
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = numberCovert(col.text)
            info_dict['Insider_id'] = cols[0].a['href'].split('oc=')[1].split('&tc=')[0]
            df = df.append(info_dict, ignore_index=True)
        self.info['inside trader'] = df
        return df

    def TickerSignal(self):
        """Get all the trading signals from finviz.

        Returns:
            ticker_signals(list): get all the ticker signals as list.
        """
        from finvizfinance.screener.ticker import Ticker
        fticker = Ticker()
        signals = ['Top Gainers', 'Top Losers', 'New High', 'New Low',
                   'Most Volatile', 'Most Active', 'Unusual Volume',
                   'Overbought', 'Oversold', 'Downgrades', 'Upgrades',
                   'Earnings Before', 'Earnings After', 'Recent Insider Buying',
                   'Recent Insider Selling', 'Major News', 'Horizontal S/R',
                   'TL Resistance', 'TL Support', 'Wedge Up', 'Wedge Down',
                   'Triangle Ascending', 'Triangle Descending', 'Wedge',
                   'Channel Up', 'Channel Down', 'Channel', 'Double Top',
                   'Double Bottom', 'Multiple Top', 'Multiple Bottom',
                   'Head & Shoulders', 'Head & Shoulders Inverse']
        ticker_signal = []
        for signal in signals:
            fticker.set_filter(signal=signal, ticker=self.ticker.upper())
            if fticker.ScreenerView(verbose=0) == [self.ticker.upper()]:
                ticker_signal.append(signal)
        return ticker_signal

    def TickerFullInfo(self):
        """Get all the ticker information.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        self.TickerFundament()
        self.TickerOuterRatings()
        self.TickerNews()
        self.TickerInsideTrader()
        return self.info


class Statements:
    """
    Getting statements of ticker

    """
    def getStatements(self, ticker, statement="I", timeframe="A"):
        """Getting statements of ticker.

        Args:
            ticker(str): ticker string
            statement(str): I(Income Statement), B(Balace Sheet), C(Cash Flow)
            timeframe(str): A(Annual), Q(Quarter)
        Returns:
            df(pandas.DataFrame): statements table
        """
        url = 'https://finviz.com/api/statement.ashx?t={ticker}&s={statement}{timeframe}'.format(ticker=ticker,
                                                                                                statement=statement,
                                                                                                timeframe=timeframe)
        try:
            website = requests.get(url, headers=headers)
            website.raise_for_status()
            response = json.loads(website.content)
            df = pd.DataFrame.from_dict(response['data'], orient='index')
            return df
        except requests.exceptions.HTTPError as err:
            raise Exception(err)