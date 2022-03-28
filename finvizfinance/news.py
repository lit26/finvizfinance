import pandas as pd
from finvizfinance.util import web_scrap

"""
.. module:: news
   :synopsis: news table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

NEWS_URL = "https://finviz.com/news.ashx"
NEWS_TABLE_INDEX = 8


class News:
    """News
    Getting information from the finviz news page.
    Args:
        news_table_index(int): table index of the news page. change only if change on finviz side.

    """

    def __init__(self, news_table_index=NEWS_TABLE_INDEX):
        """initiate module"""
        self.all_news = {}
        self.soup = web_scrap(NEWS_URL)
        self.news = {}
        self._news_table_index = news_table_index

    def get_news(self):
        """Get insider information table.

        Retrieves table information from finviz finance news.

        Returns:
            news(dict): news table

        """
        tables = self.soup.findAll("table")
        news = tables[self._news_table_index]
        news_df = self._get_news_helper(news)
        blog = tables[self._news_table_index + 1]
        blog_df = self._get_news_helper(blog)
        self.news = {"news": news_df, "blogs": blog_df}
        return self.news

    def _get_news_helper(self, rows):
        """Get insider information table helper function.

        Args:
            rows(beautiful soup): rows of website information

        Returns:
            df(pandas.DataFrame): news information table

        """
        df = pd.DataFrame([], columns=["Date", "Title", "Source", "Link"])
        rows = rows.findAll("tr")
        for row in rows:
            cols = row.findAll("td")
            date = cols[1].text
            title = cols[2].text
            link = cols[2].a["href"]
            source = link.split("/")[2]
            if source == "feedproxy.google.com":
                source = link.split("/")[4]
            df = df.append(
                {"Date": date, "Title": title, "Source": source, "Link": link},
                ignore_index=True,
            )
        return df
