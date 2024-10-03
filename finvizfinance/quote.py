"""
.. module:: quote
   :synopsis: individual ticker.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from datetime import datetime, date
import json
import pandas as pd
import requests
from finvizfinance.util import (
    web_scrap,
    image_scrap,
    number_covert,
    headers,
    format_datetime,
)

QUOTE_URL = "https://finviz.com/quote.ashx?t={ticker}"
NUM_COL = [
    "P/E",
    "EPS (ttm)",
    "Insider Own",
    "Shs Outstand",
    "Market Cap",
    "Forward P/E",
    "EPS nest Y",
    "Insider ",
]


class Quote:
    """quote
    Getting current price of the ticker

    """

    def get_current(self, ticker):
        """Getting current price of the ticker.

        Returns:
            price(float): price of the ticker
        """
        soup = web_scrap("https://finviz.com/request_quote.ashx?t={}".format(ticker))
        return soup.text


class finvizfinance:
    """finvizfinance
    Getting information from the individual ticker.

    Args:
        ticker(str): ticker string
        verbose(int): choice of visual the progress. 1 for visualize progress.
    """

    def __init__(
        self,
        ticker,
        verbose=0,
    ):
        """initiate module"""

        self.ticker = ticker
        self.flag = False
        self.quote_url = QUOTE_URL.format(ticker=ticker)
        self.soup = web_scrap(self.quote_url)
        if self._checkexist(verbose):
            self.flag = True
        self.info = {}

    def _checkexist(self, verbose):
        try:
            if "not found" in self.soup.find("td", class_="body-text").text:
                print("Ticker not found.")
                return False
        except:
            if verbose == 1:
                print("Ticker exists.")
            return True

    def ticker_charts(
        self, timeframe="daily", charttype="advanced", out_dir="", urlonly=False
    ):
        """Download ticker charts.

        Args:
            timeframe(str): choice of timeframe (daily, weekly, monthly).
            charttype(str): choice of type of chart (candle, line, advanced).
            out_dir(str): output image directory. default none.
            urlonly (bool): choice of downloading charts, default: downloading chart

        Returns:
            charturl(str): url for the chart
        """
        if timeframe not in ["daily", "weekly", "monthly"]:
            raise ValueError("Invalid timeframe '{}'".format(timeframe))
        if charttype not in ["candle", "line", "advanced"]:
            raise ValueError("Invalid chart type '{}'".format(charttype))
        url_type = "c"
        url_ta = "0"
        if charttype == "line":
            url_type = "l"
        elif (
            charttype == "advanced" and timeframe != "weekly" and timeframe != "monthly"
        ):
            url_ta = "1"

        url_timeframe = "d"
        if timeframe == "weekly":
            url_timeframe = "w"
        elif timeframe == "monthly":
            url_timeframe = "m"
        chart_url = "https://finviz.com/chart.ashx?t={ticker}&ty={type}&ta={ta}&p={timeframe}".format(
            ticker=self.ticker, type=url_type, ta=url_ta, timeframe=url_timeframe
        )
        if not urlonly:
            image_scrap(chart_url, self.ticker, out_dir)
        return chart_url

    def ticker_fundament(self, raw=True, output_format="dict"):
        """Get ticker fundament.

        Args:
            raw(boolean): if True, the data is raw.
            output_format(str): choice of output format (dict, series).

        Returns:
            fundament(dict): ticker fundament.
        """
        if output_format not in ["dict", "series"]:
            raise ValueError(
                "Invalid output format '{}'. Possible choice: {}".format(
                    output_format, ["dict", "series"]
                )
            )
        fundament_info = {}

        fundament_info["Company"] = self.soup.find(
            "h2", class_="quote-header_ticker-wrapper_company"
        ).text.strip()
        quote_links = self.soup.find("div", class_="quote-links")
        links = quote_links.find_all("a")
        fundament_info["Sector"] = links[0].text
        fundament_info["Industry"] = links[1].text
        fundament_info["Country"] = links[2].text
        fundament_info["Exchange"] = links[3].text

        fundament_table = self.soup.find("table", class_="snapshot-table2")
        rows = fundament_table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            cols = [i.text for i in cols]
            fundament_info = self._parse_column(cols, raw, fundament_info)
        self.info["fundament"] = fundament_info

        if output_format == "dict":
            return fundament_info
        return pd.DataFrame.from_dict(fundament_info, orient="index", columns=["Stat"])

    def _parse_column(self, cols, raw, fundament_info):
        header = ""
        for i, value in enumerate(cols):
            if i % 2 == 0:
                header = value
            else:
                if header == "Volatility":
                    fundament_info = self._parse_volatility(
                        header, fundament_info, value, raw
                    )
                elif header == "52W Range":
                    fundament_info = self._parse_52w_range(
                        header, fundament_info, value, raw
                    )
                elif header == "Optionable" or header == "Shortable":
                    if raw:
                        fundament_info[header] = value
                    elif value == "Yes":
                        fundament_info[header] = True
                    else:
                        fundament_info[header] = False
                else:
                    # Handle EPS Next Y keys with two different values
                    if header == "EPS next Y" and header in fundament_info.keys():
                        header += " Percentage"
                    if raw:
                        fundament_info[header] = value
                    else:
                        try:
                            fundament_info[header] = number_covert(value)
                        except ValueError:
                            fundament_info[header] = value
        return fundament_info

    def _parse_52w_range(self, header, fundament_info, value, raw):
        info_header = ["52W Range From", "52W Range To"]
        info_value = [0, 2]
        self._parse_value(header, fundament_info, value, raw, info_header, info_value)
        return fundament_info

    def _parse_volatility(self, header, fundament_info, value, raw):
        info_header = ["Volatility W", "Volatility M"]
        info_value = [0, 1]
        self._parse_value(header, fundament_info, value, raw, info_header, info_value)
        return fundament_info

    def _parse_value(self, header, fundament_info, value, raw, info_header, info_value):
        try:
            value = value.split()
            if raw:
                for i, value_index in enumerate(info_value):
                    fundament_info[info_header[i]] = value[value_index]
            else:
                for i, value_index in enumerate(info_value):
                    fundament_info[info_header[i]] = number_covert(value[value_index])
        except:
            fundament_info[header] = value
        return fundament_info

    def ticker_description(self):
        """Get ticker description.

        Returns:
            description(str): ticker description.
        """
        return self.soup.find("td", class_="fullview-profile").text

    def ticker_outer_ratings(self):
        """Get outer ratings table.

        Returns:
            df(pandas.DataFrame): outer ratings table
        """
        fullview_ratings_outer = self.soup.find("table", class_="js-table-ratings")
        frame = []
        try:
            rows = fullview_ratings_outer.find_all(
                "td", class_="fullview-ratings-inner"
            )
            if len(rows) == 0:
                rows = fullview_ratings_outer.find_all("tr")[1:]
            for row in rows:
                each_row = row.find("tr")
                if not each_row:
                    each_row = row
                cols = each_row.find_all("td")
                rating_date = cols[0].text
                if rating_date.lower().startswith("today"):
                    rating_date = date.today()
                else:
                    rating_date = datetime.strptime(rating_date, "%b-%d-%y")

                status = cols[1].text
                outer = cols[2].text
                rating = cols[3].text
                price = cols[4].text
                info_dict = {
                    "Date": rating_date,
                    "Status": status,
                    "Outer": outer,
                    "Rating": rating,
                    "Price": price,
                }
                frame.append(info_dict)
            df = pd.DataFrame(frame)
            self.info["ratings_outer"] = df
            return df
        except AttributeError:
            return None

    def ticker_news(self):
        """Get news information table.

        Returns:
            df(pandas.DataFrame): news information table
        """
        fullview_news_outer = self.soup.find("table", class_="fullview-news-outer")
        rows = fullview_news_outer.find_all("tr")
        
        frame = []
        last_date = ""
        for row in rows:
            try:
                cols = row.find_all("td")
                news_date = cols[0].text
                title = cols[1].a.text
                link = cols[1].a["href"]
                source = cols[1].span.text[1:-1]
                news_time = news_date.split()
                if len(news_time) == 2:
                    last_date = news_time[0]
                    news_time = " ".join(news_time)
                else:
                    news_time = last_date + " " + news_time[0]

                news_time = format_datetime(news_time)

                info_dict = {"Date": news_time, "Title": title, "Link": link, "Source": source}
                frame.append(info_dict)
            except AttributeError:
                pass
        df = pd.DataFrame(frame)
        self.info["news"] = df
        return df

    def ticker_inside_trader(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        inside_trader = self.soup.find("table", class_="body-table")
        rows = inside_trader.find_all("tr")
        table_header = [i.text for i in rows[0].find_all("th")]
        table_header += ["SEC Form 4 Link", "Insider_id"]
        frame = []
        rows = rows[1:]
        num_col = ["Cost", "#Shares", "Value ($)", "#Shares Total"]
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.find_all("td")
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = number_covert(col.text)
            info_dict["SEC Form 4 Link"] = cols[-1].find("a").attrs["href"]
            info_dict["Insider_id"] = cols[0].a["href"].split("oc=")[1].split("&tc=")[0]
            frame.append(info_dict)
        df = pd.DataFrame(frame)
        self.info["inside trader"] = df
        return df

    def ticker_signal(self):
        """Get all the trading signals from finviz.

        Returns:
            ticker_signals(list): get all the ticker signals as list.
        """
        from finvizfinance.screener.ticker import Ticker

        fticker = Ticker()
        signals = [
            "Top Gainers",
            "Top Losers",
            "New High",
            "New Low",
            "Most Volatile",
            "Most Active",
            "Unusual Volume",
            "Overbought",
            "Oversold",
            "Downgrades",
            "Upgrades",
            "Earnings Before",
            "Earnings After",
            "Recent Insider Buying",
            "Recent Insider Selling",
            "Major News",
            "Horizontal S/R",
            "TL Resistance",
            "TL Support",
            "Wedge Up",
            "Wedge Down",
            "Triangle Ascending",
            "Triangle Descending",
            "Wedge",
            "Channel Up",
            "Channel Down",
            "Channel",
            "Double Top",
            "Double Bottom",
            "Multiple Top",
            "Multiple Bottom",
            "Head & Shoulders",
            "Head & Shoulders Inverse",
        ]
        ticker_signal = []
        for signal in signals:
            try:
                fticker.set_filter(signal=signal, ticker=self.ticker.upper())
                if fticker.screener_view(verbose=0) == [self.ticker.upper()]:
                    ticker_signal.append(signal)
            except:
                pass
        return ticker_signal

    def ticker_full_info(self):
        """Get all the ticker information.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        self.ticker_fundament()
        self.ticker_outer_ratings()
        self.ticker_news()
        self.ticker_inside_trader()
        return self.info


class Statements:
    """
    Getting statements of ticker

    """

    def get_statements(self, ticker, statement="I", timeframe="A"):
        """Getting statements of ticker.

        Args:
            ticker(str): ticker string
            statement(str): I(Income Statement), B(Balace Sheet), C(Cash Flow)
            timeframe(str): A(Annual), Q(Quarter)
        Returns:
            df(pandas.DataFrame): statements table
        """
        url = "https://finviz.com/api/statement.ashx?t={ticker}&s={statement}{timeframe}".format(
            ticker=ticker, statement=statement, timeframe=timeframe
        )
        try:
            website = requests.get(url, headers=headers)
            website.raise_for_status()
            response = json.loads(website.content)
            df = pd.DataFrame.from_dict(response["data"], orient="index")
            return df
        except requests.exceptions.HTTPError as err:
            raise Exception(err)
