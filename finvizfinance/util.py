import requests
import pandas as pd
from bs4 import BeautifulSoup

"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

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
        raise SystemExit(err)
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
            out_dir +='/'
        f = open('{}{}.jpg'.format(out_dir, ticker), "wb")
        f.write(r.content)
        f.close()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

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