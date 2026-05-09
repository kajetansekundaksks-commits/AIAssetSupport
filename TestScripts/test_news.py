import yfinance as yf

"""
This code retrieves the latest news articles related to Apple Inc. (AAPL) using the yfinance library.
It prints the title and link of the first five news articles, separated by a line of dashes for better readability.
"""

ticker = yf.Ticker("AAPL")
news = ticker.news

for article in news[:5]:
    content = article.get("content", {})

    title = content.get("title")
    summary = content.get("summary")
    pub_date = content.get("pubDate")

    canonical_url = content.get("canonicalUrl", {})
    url = canonical_url.get("url")

    provider = content.get("provider", {})
    source = provider.get("displayName")

    print("Title:", title)
    print("Source:", source)
    print("Published:", pub_date)
    print("URL:", url)
    print("Summary:", summary)
    print("-" * 80)