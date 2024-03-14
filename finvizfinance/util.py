"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date

from finvizfinance.constants import (
    signal_dict,
    filter_dict,
    order_dict,
    CUSTOM_SCREENER_COLUMNS
)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}
session = requests.Session()

proxy_dict = None


def set_proxy(proxies):
    global proxy_dict
    proxy_dict = proxies


def get_signal():
    """Get signals.

    Returns:
        signals(list): all the available trading signals
    """
    return list(signal_dict.keys())


def get_filters():
    """Get filters.

    Returns:
        filters(list): all the available filters
    """
    return list(filter_dict.keys())


def get_filter_options(screen_filter):
    """Get filters options.

    Args:
        screen_filter(str): screen filter for checking options

    Returns:
        filter_options(list): all the available filters
    """
    if screen_filter not in filter_dict:
        filter_keys = list(filter_dict.keys())
        raise ValueError(
            "Invalid filter '{}'. Possible filter: {}".format(
                screen_filter, filter_keys
            )
        )
    return list(filter_dict[screen_filter]["option"])


def get_orders(self):
    """Get orders.

    Returns:
        orders(list): all the available orders
    """
    return list(order_dict.keys())


def get_custom_screener_columns(self):
    """Get information about the columns

    Returns:
        columns(dict): return the index and column name.
    """
    return CUSTOM_SCREENER_COLUMNS


def web_scrap(url, params=None):
    """Scrap website.

    Args:
        url(str): website
        params(dict): request parameters
    Returns:
        soup(beautiful soup): website html
    """
    print(url, params)
    try:
        website = session.get(url, params=params,
                              headers=headers, timeout=10, proxies=proxy_dict)
        website.raise_for_status()
        soup = BeautifulSoup(website.text, "lxml")
    except requests.exceptions.HTTPError as err:
        raise Exception(err)
    except requests.exceptions.Timeout as err:
        raise Exception(err)
    return soup


def image_scrap(url, ticker, out_dir):
    """scrap website and download image

    Args:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    try:
        r = session.get(url, stream=True, headers=headers, timeout=10)
        r.raise_for_status()
        r.raw.decode_content = True
        if len(out_dir) != 0:
            out_dir += "/"
        f = open("{}{}.jpg".format(out_dir, ticker), "wb")
        f.write(r.content)
        f.close()
    except requests.exceptions.HTTPError as err:
        raise Exception(err)
    except requests.exceptions.Timeout as err:
        raise Exception(err)


def scrap_function(url):
    """Scrap forex, crypto information.

    Args:
        url(str): website
    Returns:
        df(pandas.DataFrame): performance table
    """
    soup = web_scrap(url)
    table = soup.find("table", class_="groups_table")
    rows = table.find_all("tr")
    table_header = [i.text.strip() for i in rows[0].find_all("th")][1:]
    frame = []
    rows = rows[1:]
    num_col_index = [i for i in range(2, len(table_header))]
    for row in rows:
        cols = row.find_all("td")[1:]
        info_dict = {}
        for i, col in enumerate(cols):
            if i not in num_col_index:
                info_dict[table_header[i]] = col.text
            else:
                info_dict[table_header[i]] = number_covert(col.text)
        frame.append(info_dict)
    return pd.DataFrame(frame)


def image_scrap_function(url, chart, timeframe, urlonly):
    """Scrap forex, crypto information.

    Args:
        url(str): website
        chart(str): choice of chart
        timeframe (str): choice of timeframe(5M, H, D, W, M)
        urlonly (boolean):  choice of downloading chart
    """
    if timeframe == "5M":
        url += "m5"
    elif timeframe == "H":
        url += "h1"
    elif timeframe == "D":
        url += "d1"
    elif timeframe == "W":
        url += "w1"
    elif timeframe == "M":
        url += "mo"
    else:
        raise ValueError("Invalid timeframe.")

    soup = web_scrap(url)
    content = soup.find("div", class_="container")
    imgs = content.find_all("img")
    for img in imgs:
        website = img["src"]
        name = website.split("?")[1].split("&")[0].split(".")[0]
        chart_name = name.split("_")[0]
        if chart.lower() == chart_name:
            charturl = "https://finviz.com/" + website
            if not urlonly:
                image_scrap(charturl, name, "")
            return charturl
        else:
            continue


def number_covert(num):
    """covert number(str) to number(float)

    Args:
        num(str): number of string
    Return:
        num(float): number of string
    """
    if num == "-":
        return None
    elif num[-1] == "%":
        return float(num[:-1]) / 100
    elif num[-1] == "B":
        return float(num[:-1]) * 1000000000
    elif num[-1] == "M":
        return float(num[:-1]) * 1000000
    elif num[-1] == "K":
        return float(num[:-1]) * 1000
    else:
        return float("".join(num.split(",")))


def format_datetime(date_str):
    if date_str.lower().startswith("today"):
        today = date.today()
        time_str = date_str.split()[1]

        hour, minute = map(int, time_str[:-2].split(":"))
        ampm = time_str[-2:]

        if ampm.lower() == "pm" and hour != 12:
            hour += 12
        return datetime(today.year, today.month, today.day, hour, minute)
    else:
        return datetime.strptime(date_str, "%b-%d-%y %I:%M%p")


def progress_bar(page, total):
    bar_len = 30
    filled_len = int(round(bar_len * page / float(total)))
    bar = "#" * filled_len + "-" * (bar_len - filled_len)
    sys.stdout.write(
        "[Info] loading page [{}] {}/{} \r".format(bar, page, total))
    sys.stdout.flush()
