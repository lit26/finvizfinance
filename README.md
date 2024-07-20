![PyPI - Python Version](https://img.shields.io/pypi/pyversions/finvizfinance)
![PyPI](https://img.shields.io/pypi/v/finvizfinance)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/finvizfinance)
![PyPI - License](https://img.shields.io/pypi/l/finvizfinance?color=gre)
[![Coverage Status](https://coveralls.io/repos/github/lit26/finvizfinance/badge.svg)](https://coveralls.io/github/lit26/finvizfinance)
![Read the Docs](https://img.shields.io/readthedocs/finvizfinance)
[![Downloads](https://pepy.tech/badge/finvizfinance)](https://pepy.tech/project/finvizfinance)
[![CodeFactor](https://www.codefactor.io/repository/github/lit26/finvizfinance/badge/master)](https://www.codefactor.io/repository/github/lit26/finvizfinance/overview/master)
[![Donate PayPal](https://img.shields.io/badge/Donate%20%24-PayPal-brightgreen.svg)](https://www.paypal.me/TIANNINGL/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# finvizfinance

finvizfinance is a package which collects financial information from FinViz website. The package provides the information of the following:

- Stock charts, fundamental & technical information, insider information and stock news
- Forex charts and performance
- Crypto charts and performance

Screener and Group provide dataframes for comparing stocks according to different filters and trading signals.

Docs: https://finvizfinance.readthedocs.io/en/latest/

### Downloads

To download the latest version from GitHub:

```
$ git clone https://github.com/lit26/finvizfinance.git
```

Or install from PyPi:

```
$ pip install finvizfinance
```

### Quote

Getting information (fundament, description, outer rating, stock news, inside trader) of an individual stock.

```python
from finvizfinance.quote import finvizfinance

stock = finvizfinance('tsla')
```

#### Chart

```python
stock.ticker_charts()
```

#### Fundament

```python
stock_fundament = stock.ticker_fundament()

# result
# stock_fundament = {'Company': 'Tesla, Inc.', 'Sector': 'Consumer Cyclical',
# 'Industry': 'Auto Manufacturers', 'Country': 'USA', 'Index': '-', 'P/E': '849.57',
# 'EPS (ttm)': '1.94', 'Insider Own': '0.10%', 'Shs Outstand': '186.00M',
# 'Perf Week': '13.63%', 'Market Cap': '302.10B', 'Forward P/E': '106.17',
# ...}
```

#### Description

```python
stock_description = stock.ticker_description()

# stock_description
# stock_description = 'Tesla, Inc. designs, develops, manufactures, ...'
```

#### Outer Ratings

```python
outer_ratings_df = stock.ticker_outer_ratings()
```

![Outer Ratings example](asset/outer_rating.png)

#### Stock News

```python
news_df = stock.ticker_news()
```

![stock news example](asset/stock_news.png)

#### Inside Trader

```python
inside_trader_df = stock.ticker_inside_trader()
```

![insider trader example](asset/insider_trader.png)

### News

Getting recent financial news from finviz.

```python
from finvizfinance.news import News

fnews = News()
all_news = fnews.get_news()
```

Finviz News include 'news' and 'blogs'.

```python
all_news['news'].head()
```

![news example](asset/news_news.png)

```python
all_news['blogs'].head()
```

![news example](asset/news_blogs.png)

### Insider

Getting insider trading information.

```python
from finvizfinance.insider import Insider

finsider = Insider(option='top owner trade')
# option: latest, top week, top owner trade
# default: latest

insider_trader = finsider.get_insider()
```

![insider example](asset/insider.png)

### Screener (Overview, Valuation, Financial, Ownership, Performance, Technical)

Getting multiple tickers' information according to the filters.

#### Example: Overview

```python
from finvizfinance.screener.overview import Overview

foverview = Overview()
filters_dict = {'Index':'S&P 500','Sector':'Basic Materials'}
foverview.set_filter(filters_dict=filters_dict)
df = foverview.screener_view()
df.head()
```

![insider example](asset/screen_overview.png)

### Screener (Ticker)

Getting list of tickers according to the filters.

### Misc (Proxy)

Optional proxy can be used for getting information from FinViz website. Accessible from finvizfinance
it's an extension of requests library proxies

```python
from finvizfinance.util import set_proxy

proxies={'http': 'http://127.0.0.1:8080'}
set_proxy(proxies)
```

### Credit

Developed by Tianning Li. Feel free to give comments or suggestions.
