from finvizfinance.webrequest import webScrap
import pandas as pd

NEWS_URL = 'https://finviz.com/news.ashx'

class finviznews:
    def __init__(self):
        self.all_news = {}
        self.soup = webScrap(NEWS_URL)
        self.news = {}

    def getNews(self):
        tables = self.soup.findAll('table')
        news = tables[6]
        news_df = self._getNewsHelper(news)
        blog = tables[7]
        blog_df = self._getNewsHelper(blog)
        self.news = {'news':news_df, 'blogs':blog_df}
        return self.news

    def _getNewsHelper(self, rows):
        df = pd.DataFrame([], columns=['Date', 'Title', 'Link'])
        rows = rows.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            date = cols[1].text
            title = cols[2].text
            link = cols[2].a['href']
            df = df.append({'Date': date, 'Title': title, 'Link': link},
                           ignore_index=True)
        return df

