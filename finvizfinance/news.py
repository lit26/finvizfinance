"""
.. module:: news
   :synopsis: news table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from finvizfinance.exceptions import FinvizParseError
from finvizfinance.util import require, web_scrap

NEWS_URL = "https://finviz.com/news.ashx"


class News:
    """News
    Getting information from the finviz news page.
    """

    def __init__(self) -> None:
        """initiate module"""
        self.all_news: dict = {}
        self.soup = web_scrap(NEWS_URL)
        self.news: dict[str, pd.DataFrame] = {}

    def get_news(self) -> dict[str, pd.DataFrame]:
        """Get insider information table.

        Retrieves table information from finviz finance news.

        Returns:
            news(dict): news table

        """
        news_div = require(self.soup.find(id="news"), NEWS_URL, "#news")
        news_content = require(news_div.find("table"), NEWS_URL, "#news > table")
        tr_list = news_content.find_all("tr", recursive=False)
        if len(tr_list) < 2:
            raise FinvizParseError(url=NEWS_URL, selector="#news table rows")
        news_collection = tr_list[1]
        tables = news_collection.find_all("table")
        if len(tables) < 2:
            raise FinvizParseError(url=NEWS_URL, selector="#news news/blogs tables")

        news_df = self._get_news_helper(tables[0])
        blog_df = self._get_news_helper(tables[1])
        self.news = {"news": news_df, "blogs": blog_df}
        return self.news

    def _get_news_helper(self, rows: Any) -> pd.DataFrame:
        """Get insider information table helper function.

        Args:
            rows(beautiful soup): rows of website information

        Returns:
            df(pandas.DataFrame): news information table

        """
        table = []
        rows = rows.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3 or cols[2].a is None:
                # Empty / malformed news line; skip explicitly (no silent hide).
                continue
            date = cols[1].text
            title = cols[2].text
            link = cols[2].a["href"]
            source = link.split("/")[2]
            if source == "feedproxy.google.com":
                source = link.split("/")[4]
            info_dict = {
                "Date": date,
                "Title": title,
                "Source": source,
                "Link": link,
            }
            table.append(info_dict)
        return pd.DataFrame(table)
