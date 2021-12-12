def test_finvizfinance_news():
    from finvizfinance.news import News
    fnews = News()
    all_news = fnews.get_news()
    news = all_news['news']
    blogs = all_news['blogs']
    assert(news is not None)
    assert(blogs is not None)