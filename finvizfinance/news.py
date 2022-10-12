"""
.. module:: news
   :synopsis: news table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import pandas as pd
from finvizfinance.util import web_scrap

NEWS_URL = "https://finviz.com/news.ashx"


class News:
    """News
    Getting information from the finviz news page.
    """

    def __init__(self):
        """initiate module"""
        self.all_news = {}
        self.soup = web_scrap(NEWS_URL)
        self.news = {}

    def get_news(self):
        """Get insider information table.

        Retrieves table information from finviz finance news.

        Returns:
            news(dict): news table

        """
        news_content = self.soup.find(id="news").find("table")
        news_collection = news_content.findAll("tr", recursive=False)[1]
        tables = news_collection.findAll("table")

        news = tables[0]
        news_df = self._get_news_helper(news)
        blog = tables[1]
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
        table = []
        rows = rows.findAll("tr")
        for row in rows:
            try:
                cols = row.findAll("td")
                date = cols[1].text
                title = cols[2].text
                link = cols[2].a["href"]
                source = link.split("/")[2]
                if source == "feedproxy.google.com":
                    source = link.split("/")[4]
                info_dict = {"Date": date, "Title": title, "Source": source, "Link": link}
                table.append(info_dict)
            except TypeError:
                # Empty news line
                pass
        return pd.DataFrame(table)
