from finvizfinance.util import webScrap
import pandas as pd
"""
Module:         news
Description:    Getting information from the finviz news page.
Author:         Tianning Li
"""

NEWS_URL = 'https://finviz.com/news.ashx'

class News:
    def __init__(self):
        """initiate module
        """
        self.all_news = {}
        self.soup = webScrap(NEWS_URL)
        self.news = {}

    def getNews(self):
        """Get insider information table.

        Returns:
            dict('news':pandas.DataFrame,'blogs':pandas.DataFrame):
                news information table, blogs information table
        """
        tables = self.soup.findAll('table')
        news = tables[6]
        news_df = self._getNewsHelper(news)
        blog = tables[7]
        blog_df = self._getNewsHelper(blog)
        self.news = {'news':news_df, 'blogs':blog_df}
        return self.news

    def _getNewsHelper(self, rows):
        """Get insider information table helper function.

        Parameters:
            rows(beautiful soup): rows of website information
        Returns:
            df(pandas.DataFrame): news information table
        """
        df = pd.DataFrame([], columns=['Date', 'Title','Source','Link'])
        rows = rows.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            date = cols[1].text
            title = cols[2].text
            link = cols[2].a['href']
            source = link.split('/')[2]
            if source == 'feedproxy.google.com':
                source = link.split('/')[4]
            df = df.append({'Date': date, 'Title': title, 'Source':source, 'Link': link},
                           ignore_index=True)
        return df

