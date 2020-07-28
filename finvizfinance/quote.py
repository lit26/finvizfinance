from finvizfinance.util import webScrap, numberCovert
import pandas as pd
from datetime import datetime

QUOTE_URL = 'https://finviz.com/quote.ashx?t={ticker}'

class finvizfinance:
    def __init__(self,ticker):
        self.ticker = ticker
        self.flag = False
        self.quote_url = QUOTE_URL.format(ticker=ticker)
        self.soup = webScrap(self.quote_url)
        if self._checkexist():
            self.flag = True
        self.info = {}

    def _checkexist(self):
        try:
            if 'not found' in self.soup.find('td', class_='body-text').text:
                print('Ticker not found.')
                return False
        except:
            print('Ticker exists.')
            return True

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
        inside_trader = self.soup.find('table', class_='body-table')
        rows = inside_trader.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        num_col = ['Cost','#Shares','Value ($)','#Shares Total']
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.findAll('td')
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = numberCovert(col.text)
            df = df.append(info_dict, ignore_index=True)
        self.info['inside trader'] = df
        return df

    def TickerFullInfo(self):
        self.TickerFundament()
        self.TickerOuterRatings()
        self.TickerNews()
        self.TickerInsideTrader()
        return self.info

if __name__ == '__main__':
    tsla = finvizfinance('tsla')
    tsla_info = tsla.TickerFullInfo()
    print(tsla_info['inside trader'][:5])





