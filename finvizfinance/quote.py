"""
.. module:: quote
   :synopsis: individual ticker.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from datetime import datetime, date
import re
import pandas as pd
from finvizfinance.util import (
    web_scrap,
    web_scrap_json,
    image_scrap,
    number_convert,
    format_datetime,
    require,
    optional,
    warn_missing,
)
from finvizfinance.exceptions import FinvizParseError

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
        body = self.soup.find("td", class_="body-text")
        if body is not None and "not found" in body.text:
            print("Ticker not found.")
            return False
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

    def _extract_classification(self):
        """Sector / Industry / Country / Exchange from the quote-links region.

        These are optional (an ETF has none). Resilient to the region being
        renamed (Drift): falls back to the stable screener-filter anchors, and
        finally returns ``None`` with a warning for anything genuinely absent.
        """
        keys = ["Sector", "Industry", "Country", "Exchange"]
        result = {k: None for k in keys}

        quote_links = self.soup.find("div", class_="quote-links")
        if quote_links is not None:
            anchors = quote_links.find_all("a")
            for i, key in enumerate(keys):
                if i < len(anchors):
                    result[key] = anchors[i].text.strip()

        # Drift fallback: match the classification anchors by their filter href.
        href_tokens = {
            "Sector": "f=sec_",
            "Industry": "f=ind_",
            "Country": "f=geo_",
            "Exchange": "f=exch_",
        }
        for key, token in href_tokens.items():
            if result[key]:
                continue
            anchor = self.soup.find("a", href=re.compile(re.escape(token)))
            if anchor is not None:
                result[key] = anchor.text.strip()

        # Missing-field semantics: warn and keep None for anything still absent.
        for key in keys:
            if result[key] is None:
                warn_missing(
                    self.quote_url, "quote classification link ({})".format(key)
                )
        return result

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

        fundament_info["Company"] = require(
            self.soup.find("h2", class_="quote-header_ticker-wrapper_company"),
            self.quote_url,
            "h2.quote-header_ticker-wrapper_company",
        ).text.strip()

        fundament_info.update(self._extract_classification())

        fundament_table = require(
            self.soup.find("table", class_="snapshot-table2"),
            self.quote_url,
            "table.snapshot-table2",
        )
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
                            fundament_info[header] = number_convert(value)
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
        value = value.split()
        if len(value) <= max(info_value):
            # Unexpected shape for this datum; keep the raw split, do not crash.
            fundament_info[header] = value
            return fundament_info
        if raw:
            for i, value_index in enumerate(info_value):
                fundament_info[info_header[i]] = value[value_index]
        else:
            for i, value_index in enumerate(info_value):
                fundament_info[info_header[i]] = number_convert(value[value_index])
        return fundament_info

    def ticker_description(self):
        """Get ticker description.

        Returns:
            description(str): ticker description.
        """
        return require(
            self.soup.find("td", class_="fullview-profile")
            or self.soup.find(class_="fullview-profile"),
            self.quote_url,
            "fullview-profile",
        ).text

    def _ticker_list_from_link(self, label, selector):
        """Extract a comma-separated ticker list from a quote-page link.

        Finds an anchor whose visible text is ``label`` (case-insensitive) and
        parses its ``t=`` query into a ticker list. Returns ``[]`` with a
        warning when the link is absent (an optional feature, not a Drift).
        """
        link = self.soup.find("a", string=label)
        if not link:
            link = self.soup.find(
                "a", string=re.compile(r"^\s*{}\s*$".format(label), re.IGNORECASE)
            )
        if not link:
            warn_missing(self.quote_url, selector)
            return []

        href = link.get("href", "")
        if "t=" not in href:
            return []
        tickers_part = href.split("t=")[-1]
        return [t.strip() for t in tickers_part.split(",") if t.strip()]

    def ticker_peer(self):
        """Get peer tickers for the given ticker.

        Returns:
            list: A list of peer ticker symbols (str). Returns an empty list if not found.
        """
        return self._ticker_list_from_link("Peers", "Peers link")

    def ticker_etf_holders(self):
        """Get ETFs that hold the given ticker.

        Returns:
        list: A list of ETF ticker symbols (str) that include the given ticker
        in their holdings. Returns an empty list if not found.
        """
        return self._ticker_list_from_link("Held by", "Held by link")

    def ticker_outer_ratings(self):
        """Get outer ratings table.

        Returns:
            df(pandas.DataFrame): outer ratings table, or None if absent.
        """
        fullview_ratings_outer = optional(
            self.soup.find("table", class_="js-table-ratings"),
            self.quote_url,
            "table.js-table-ratings",
        )
        if fullview_ratings_outer is None:
            self.info["ratings_outer"] = None
            return None

        rows = fullview_ratings_outer.find_all("td", class_="fullview-ratings-inner")
        if len(rows) == 0:
            rows = fullview_ratings_outer.find_all("tr")[1:]
        frame = []
        for row in rows:
            each_row = row.find("tr")
            if not each_row:
                each_row = row
            cols = each_row.find_all("td")
            if len(cols) < 5:
                continue
            rating_date = cols[0].text
            if rating_date.lower().startswith("today"):
                rating_date = date.today()
            else:
                rating_date = datetime.strptime(rating_date, "%b-%d-%y")
            info_dict = {
                "Date": rating_date,
                "Status": cols[1].text,
                "Outer": cols[2].text,
                "Rating": cols[3].text,
                "Price": cols[4].text,
            }
            frame.append(info_dict)
        df = pd.DataFrame(frame)
        self.info["ratings_outer"] = df
        return df

    def ticker_news(self):
        """Get news information table.

        Returns:
            df(pandas.DataFrame): news information table, or None if absent.
        """
        fullview_news_outer = optional(
            self.soup.find("table", class_="fullview-news-outer"),
            self.quote_url,
            "table.fullview-news-outer",
        )
        if fullview_news_outer is None:
            self.info["news"] = None
            return None
        rows = fullview_news_outer.find_all("tr")

        frame = []
        last_date = ""
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2 or cols[1].a is None:
                # Malformed / empty news line; skip explicitly (no silent hide).
                continue
            news_date = cols[0].text
            title = cols[1].a.text
            link = cols[1].a["href"]
            source = cols[1].span.text[1:-1] if cols[1].span else ""
            news_time = news_date.split()
            if len(news_time) == 2:
                last_date = news_time[0]
                news_time = " ".join(news_time)
            else:
                news_time = last_date + " " + news_time[0]
            news_time = format_datetime(news_time)

            info_dict = {
                "Date": news_time,
                "Title": title,
                "Link": link,
                "Source": source,
            }
            frame.append(info_dict)
        df = pd.DataFrame(frame)
        self.info["news"] = df
        return df

    def ticker_inside_trader(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table, or None if absent.
        """
        inside_trader = optional(
            self.soup.find("table", class_="body-table"),
            self.quote_url,
            "table.body-table",
        )
        if inside_trader is None:
            self.info["inside trader"] = None
            return None
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
                    info_dict[table_header[i]] = number_convert(col.text)
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
            # Let typed errors (a Wall or a Drift in the screener) surface rather
            # than silently dropping signals — the previous bare `except: pass`
            # hid real failures.
            fticker.set_filter(signal=signal, ticker=self.ticker.upper())
            if fticker.screener_view(verbose=0) == [self.ticker.upper()]:
                ticker_signal.append(signal)
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
        response = web_scrap_json(url)
        if "data" not in response:
            raise FinvizParseError(url=url, selector="json:data")
        df = pd.DataFrame.from_dict(response["data"], orient="index")
        return df
