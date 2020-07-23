# finvizfinance

Fetch information from finviz

```python
import finvizfinance
import pandas as pd

stock = finvizfinance('tsla')
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
stock_description = 'Tesla, Inc. designs, develops, manufactures, ...'
```

#### Outer Ratings
```python
outer_ratings_df = stock.TickerOuterRatings()
``` 

#### Stock News
```python
news_df = stock.TickerNews()
```

#### Inside Trader
```python
inside_trader_df = stock.TickerInsideTrader()
```
