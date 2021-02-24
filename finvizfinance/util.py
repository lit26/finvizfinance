import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys

"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

NUMBER_COL = ['Market Cap', 'P/E', 'Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/C',
              'P/FCF', 'Dividend', 'Payout Ratio', 'EPS', 'EPS this Y', 'EPS next Y',
              'EPS past 5Y', 'EPS next 5Y', 'Sales past 5Y', 'EPS Q/Q', 'Sales Q/Q',
              'Outstanding', 'Float', 'Insider Own', 'Insider Trans', 'Inst Own', 'Inst Trans',
              'Float Short', 'Short Ratio', 'ROA', 'ROE', 'ROI', 'Curr R', 'Quick R', 'LTDebt/Eq',
              'Debt/Eq', 'Gross M', 'Oper M', 'Profit M', 'Perf Week', 'Perf Month', 'Perf Quart',
              'Perf Half', 'Perf Year', 'Perf YTD', 'Beta', 'ATR', 'Volatility W', 'Volatility M',
              'SMA20', 'SMA50', 'SMA200', '50D High', '50D Low', '52W High', '52W Low', 'RSI',
              'from Open', 'Gap', 'Recom', 'Avg Volume', 'Rel Volume', 'Price', 'Change', 'Volume',
              'Target Price']


def webScrap(url):
    """Scrap website.

    Args:
        url(str): website
    Returns:
        soup(beautiful soup): website html
    """
    try:
        website = requests.get(url, headers=headers)
        website.raise_for_status()
        soup = BeautifulSoup(website.text, 'lxml')
    except requests.exceptions.HTTPError as err:
        raise Exception(err)
    return soup


def imageScrap(url, ticker, out_dir):
    """scrap website and download image

    Args:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    try:
        r = requests.get(url, stream=True, headers=headers)
        r.raise_for_status()
        r.raw.decode_content = True
        if len(out_dir) != 0:
            out_dir += '/'
        f = open('{}{}.jpg'.format(out_dir, ticker), "wb")
        f.write(r.content)
        f.close()
    except requests.exceptions.HTTPError as err:
        raise Exception(err)


def scrapFunction(url):
    """Scrap forex, crypto information.

    Args:
        url(str): website
    Returns:
        df(pandas.DataFrame): performance table
    """
    soup = webScrap(url)
    table = soup.findAll('table')[3]
    rows = table.findAll('tr')
    table_header = [i.text.strip() for i in rows[0].findAll('td')][1:]
    df = pd.DataFrame([], columns=table_header)
    rows = rows[1:]
    num_col_index = [i for i in range(2, len(table_header))]
    for row in rows:
        cols = row.findAll('td')[1:]
        info_dict = {}
        for i, col in enumerate(cols):
            if i not in num_col_index:
                info_dict[table_header[i]] = col.text
            else:
                info_dict[table_header[i]] = numberCovert(col.text)
        df = df.append(info_dict, ignore_index=True)
    return df


def imageScrapFunction(url, chart, timeframe, urlonly):
    """Scrap forex, crypto information.

    Args:
        url(str): website
        chart(str): choice of chart
        timeframe (str): choice of timeframe(5M, H, D, W, M)
    """
    if timeframe == '5M':
        url += 'm5'
    elif timeframe == 'H':
        url += 'h1'
    elif timeframe == 'D':
        url += 'd1'
    elif timeframe == 'W':
        url += 'w1'
    elif timeframe == 'M':
        url += 'mo'
    else:
        raise ValueError('Invalid timeframe.')

    soup = webScrap(url)
    content = soup.find('div', class_='container')
    imgs = content.findAll('img')
    for img in imgs:
        website = img['src']
        name = website.split('?')[1].split('&')[0].split('.')[0]
        chart_name = name.split('_')[0]
        if chart.lower() == chart_name:
            charturl = 'https://finviz.com/' + website
            if not urlonly:
                imageScrap(charturl, name, '')
            return charturl
        else:
            continue


def numberCovert(num):
    """covert number(str) to number(float)

    Args:
        num(str): number of string
    Return:
        num(float): number of string
    """
    if num == '-':
        return None
    elif num[-1] == '%':
        return float(num[:-1]) / 100
    elif num[-1] == 'B':
        return float(num[:-1]) * 1000000000
    elif num[-1] == 'M':
        return float(num[:-1]) * 1000000
    elif num[-1] == 'K':
        return float(num[:-1]) * 1000
    else:
        return float(''.join(num.split(',')))


def progressBar(page, total):
    bar_len = 30
    filled_len = int(round(bar_len * page / float(total)))
    bar = '#' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[Info] loading page [{}] {}/{} \r'.format(bar, page, total))
    sys.stdout.flush()