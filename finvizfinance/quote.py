from finvizfinance.webrequest import webScrap
import pandas as pd
from datetime import datetime

QUOTE_URL = 'https://finviz.com/quote.ashx?t={ticker}'

class finvizfinance:
    def __init__(self,ticker):
        self.ticker = ticker
        self.quote_url = QUOTE_URL.format(ticker=ticker)
        self.soup = webScrap(self.quote_url)
        self.info = {}

    def TickerFundament(self):
        fundament_table = self.soup.find('table', class_='snapshot-table2')
        fundament_info = {}
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
        return self.soup.find('td',class_='fullview-profile').text

    def TickerOuterRatings(self):
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
        fullview_news_outer = self.soup.find('table', class_='fullview-news-outer')
        rows = fullview_news_outer.findAll('tr')

        last_date = ''
        df = pd.DataFrame([], columns=['Date', 'Title'])
        for row in rows:
            cols = row.findAll('td')
            date = cols[0].text
            title = cols[1].a.text
            newsTime = date.split()
            if len(newsTime) == 2:
                last_date = newsTime[0]
                newsTime = ' '.join(newsTime)
            else:
                newsTime = last_date + ' ' + newsTime[0]
            newsTime = datetime.strptime(newsTime, '%b-%d-%y %I:%M%p')
            df = df.append({'Date': newsTime, 'Title': title}, ignore_index=True)
        self.info['news'] = df
        return df

    def TickerInsideTrader(self):
        inside_trader = self.soup.find('table', class_='body-table')
        rows = inside_trader.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        for row in rows:
            cols = row.findAll('td')
            insider_trading = cols[0].text
            relationship = cols[1].text
            date = cols[2].text
            transaction = cols[3].text
            cost = cols[4].text
            cost = float(cost)
            n_shares = cols[5].text
            n_shares = float(''.join(n_shares.split(',')))
            value = cols[6].text
            value = float(''.join(value.split(',')))
            n_shares_total = cols[7].text
            n_shares_total = float(''.join(n_shares_total.split(',')))
            sec_form = cols[8].text
            df = df.append({'Insider Trading': insider_trading,
                            'Relationship': relationship,
                            'Date': date,
                            'Transaction': transaction,
                            'Cost': cost,
                            '#Shares': n_shares,
                            'Value ($)': value,
                            '#Shares Total': n_shares_total,
                            'SEC Form 4': sec_form}, ignore_index=True)
        self.info['inside trader'] = df
        return df

    def TickerFullInfo(self):
        self.TickerFundament()
        self.TickerOuterRatings()
        self.TickerNews()
        self.TickerInsideTrader()
        return self.info





