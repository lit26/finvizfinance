.. Finviz Finance in Python documentation master file, created by
   sphinx-quickstart on Tue Apr 10 15:47:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Finviz Finance in Python's documentation!
================================================================

It is a Finviz Finance information downloader.

Installation (python >= v3.5)
=============================

.. code-block:: bash

    > virtualenv -p python3 virtualenvironment
    > source virtualenvironment/bin/activate
    > pip install finvizfinance

Quote Examples
==================

.. code-block:: python

   import pandas as pd
   from finvizfinance.quote import finvizfinance

   stock = finvizfinance('tsla')

Example downloading chart:

.. code-block:: python

   stock.TickerCharts(out_dir='asset')

Example getting individual ticker information

.. code-block:: python

   stock_fundament = stock.TickerFundament()
   stock_description = stock.TickerDescription()
   outer_ratings_df = stock.TickerOuterRatings()
   news_df = stock.TickerNews()
   inside_trader_df = stock.TickerInsideTrader()

Screener Example
================

.. code-block:: python

   from finvizfinance.screener.overview import Overview
   foverview = Overview()
   filters_dict = {'Exchange':'AMEX','Sector':'Basic Materials'}
   foverview.set_filter(filters_dict=filters_dict)
   df = foverview.ScreenerView()
   df.head()

News Example
============

.. code-block:: python

   from finvizfinance.news import News
   fnews = News()
   all_news = fnews.getNews()
   # all_news['news'].head()
   # all_news['blogs'].head()

Insider Example
===============

.. code-block:: python

   from finvizfinance.insider import Insider
   finsider = Insider(option='top owner trade')
   finsider.getInsider().head()

Contents
==================
.. toctree::
   Quote <quote>
   Screener <screener>
   Group <group>
   News <news>
   Insider <insider>
   Forex <forex>
   Crypto <crypto>
   Future <future>
   Earnings <earnings>
   Calendar <calendar>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`