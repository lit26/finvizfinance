![PyPI - Python Version](https://img.shields.io/pypi/pyversions/finvizfinance)
![PyPI](https://img.shields.io/pypi/v/finvizfinance)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/finvizfinance)
![PyPI - License](https://img.shields.io/pypi/l/finvizfinance?color=gre)
![Travis (.org)](https://img.shields.io/travis/lit26/finvizfinance)
![Read the Docs](https://img.shields.io/readthedocs/finvizfinance)

# finvizfinance

Fetch information from finviz

Docs: https://finvizfinance.readthedocs.io/en/latest/

### Quote

Getting information (fundament, description, outer rating, stock news, inside trader) of an individual stock.

```python
import pandas as pd
from finvizfinance.quote import finvizfinance

stock = finvizfinance('tsla')
```

#### Chart
```python
stock.TickerCharts()
```

#### Fundament
```python
stock_fundament = stock.TickerFundament()

# result
# stock_fundament = {'Index': '-',
#  'P/E': '-',
#  'EPS (ttm)': '-0.87',
#  'Insider Own': '0.10%',
#  'Shs Outstand': '183.00M',
#  'Perf Week': '3.00%',
#  'Market Cap': '295.14B',
#  'Forward P/E': '135.32',
#  'EPS next Y': '131.09%',
#  'Insider Trans': '-33.47%',
#  'Shs Float': '147.41M',
#  'Perf Month': '60.14%',
#  'Income': '-144.30M',...}
```

#### Description
```python
stock_description = stock.TickerDescription()

# stock_description
# stock_description = 'Tesla, Inc. designs, develops, manufactures, ...'
```

#### Outer Ratings
```python
outer_ratings_df = stock.TickerOuterRatings()
``` 
![Outer Ratings example](asset/outer_rating.png)
#### Stock News
```python
news_df = stock.TickerNews()
```
![stock news example](asset/stock_news.png)

#### Inside Trader
```python
inside_trader_df = stock.TickerInsideTrader()
```
![insider trader example](asset/insider_trader.png)

### News

Getting recent financial news from finviz.

```python
from finvizfinance.news import finviznews

fnews = finviznews()
all_news = fnews.getNews()
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

insider_trader = finsider.getInsider()
```
![insider example](asset/insider.png)

### Screener (Overview, Valuation, Financial, Ownership, Performance, Technical)

Getting multiple tickers' information according to the filters.

#### Example: Overview

```python
from finvizfinance.screener.overview import Overview

foverview = Overview()
filters_dict = {'Index':'S&P 500','Sector':'Basic Materials'}
foverview.set_filter(filters_dict)
df = foverview.ScreenerView()
df.head()
```
![insider example](asset/screen_overview.png)

### Screener (Ticker)

Getting list of tickers according to the filters.

