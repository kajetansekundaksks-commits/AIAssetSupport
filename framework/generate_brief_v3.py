import pyodbc
from datetime import date
from collections import defaultdict, Counter

# -----------------------------------
# SQL CONNECTION
# -----------------------------------

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

# -----------------------------------
# SETTINGS
# -----------------------------------

brief_date = str(date.today())

# -----------------------------------
# GET DATA FOR ALL INVESTORS
# -----------------------------------

query = """
SELECT
    i.InvestorID,
    i.FirstName,
    i.LastName,
    i.Email,
    p.PortfolioName,
    c.Ticker,
    c.CompanyName,
    c.Sector,

    m.TradeDate,
    m.LastPrice,
    m.LastPriceTime,
    m.OpenPrice,
    m.HighPrice,
    m.LowPrice,
    m.ClosePrice,
    m.Volume,

    n.NewsID,
    n.Title,
    n.Content,
    n.Source,
    n.PublishedAt,
    n.RelevanceScore,
    n.RelevanceMethod,
    n.TfidfSimilarity,

    s.SentimentLabel,
    s.SentimentScore
FROM Investors i
JOIN Portfolios p
    ON i.InvestorID = p.InvestorID
JOIN PortfolioHoldings ph
    ON p.PortfolioID = ph.PortfolioID
JOIN Companies c
    ON ph.CompanyID = c.CompanyID
LEFT JOIN News n
    ON c.CompanyID = n.CompanyID
LEFT JOIN SentimentAnalysis s
    ON n.NewsID = s.NewsID
OUTER APPLY (
    SELECT TOP 1
        md.TradeDate,
        md.LastPrice,
        md.LastPriceTime,
        md.OpenPrice,
        md.HighPrice,
        md.LowPrice,
        md.ClosePrice,
        md.Volume
    FROM dbo.MarketData md
    WHERE md.CompanyID = c.CompanyID
    ORDER BY md.TradeDate DESC
) m
WHERE n.NewsID IS NOT NULL
  AND n.RelevanceScore >= 2
ORDER BY
    i.InvestorID,
    c.Ticker,
    n.RelevanceScore DESC,
    n.TfidfSimilarity DESC,
    s.SentimentScore DESC,
    n.PublishedAt DESC;
"""

cursor.execute(query)
rows = cursor.fetchall()

if not rows:
    print("No relevant news found for any investor.")
    cursor.close()
    conn.close()
    raise SystemExit

# -----------------------------------
# GROUP DATA BY INVESTOR
# -----------------------------------

investors = defaultdict(list)

for row in rows:
    investors[row.InvestorID].append(row)

# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------

def get_dominant_sentiment(sentiments):
    if not sentiments:
        return "not analyzed"

    counts = Counter(sentiments)
    return counts.most_common(1)[0][0]


def get_portfolio_tone(sentiments):
    if not sentiments:
        return "not analyzed"

    counts = Counter(sentiments)

    positive = counts.get("positive", 0)
    negative = counts.get("negative", 0)
    neutral = counts.get("neutral", 0)

    if positive > negative and positive >= neutral:
        return "mostly positive"
    if negative > positive and negative >= neutral:
        return "mostly negative"
    if neutral >= positive and neutral >= negative:
        return "mostly neutral"

    return "mixed"


def get_sector_tone(sentiments):
    if not sentiments:
        return "not analyzed"

    counts = Counter(sentiments)

    positive = counts.get("positive", 0)
    negative = counts.get("negative", 0)
    neutral = counts.get("neutral", 0)

    if positive > negative and positive >= neutral:
        return "mostly positive"
    if negative > positive and negative >= neutral:
        return "mostly negative"
    if neutral >= positive and neutral >= negative:
        return "mostly neutral"

    return "mixed"

def calculate_sector_exposure(company_news):

    sector_counts = Counter()

    total_companies = len(company_news)

    for (_, _, sector) in company_news.keys():

        sector_name = sector or "Unknown"

        sector_counts[sector_name] += 1

    exposures = {}

    for sector_name, count in sector_counts.items():

        percentage = round((count / total_companies) * 100)

        exposures[sector_name] = percentage

    return exposures

def format_datetime(value):
    if value is None:
        return "N/A"

    return str(value).split(".")[0]


def format_price(value):
    if value is None:
        return "N/A"

    return f"{float(value):.2f}"


def format_volume(value):
    if value is None:
        return "N/A"

    return f"{int(value):,}"

def format_daily_move(open_price, close_price):
    if open_price is None or close_price is None or open_price == 0:
        return "N/A"

    move = ((float(close_price) - float(open_price)) / float(open_price)) * 100

    sign = "+" if move >= 0 else ""

    return f"{sign}{move:.2f}%"

def build_takeaway(ticker, sentiment, articles):
    top_titles = " ".join([a["title"].lower() for a in articles[:3]])

    if sentiment == "positive":
        base = (
            f"Coverage around {ticker} is currently constructive. "
            "The main signal is favorable media attention around recent developments."
        )
    elif sentiment == "negative":
        base = (
            f"Coverage around {ticker} is currently cautious. "
            "This holding may require closer monitoring in the next update cycle."
        )
    elif sentiment == "neutral":
        base = (
            f"Coverage around {ticker} is mostly informational. "
            "There is no clear positive or negative media signal at this stage."
        )
    else:
        base = f"Coverage around {ticker} has not been fully analyzed yet."

    if "ai" in top_titles:
        base += " AI-related developments appear to be one of the key themes."
    if "data center" in top_titles or "infrastructure" in top_titles:
        base += " Infrastructure and data center investment are also visible themes."
    if "chip" in top_titles or "semiconductor" in top_titles:
        base += " Semiconductor and supply-chain topics are present in the coverage."
    if "acquisition" in top_titles:
        base += " M&A or acquisition-related discussion appears in the news flow."
    if "safety" in top_titles or "security" in top_titles:
        base += " Risk management, safety, or security concerns are also worth watching."

    return base


# -----------------------------------
# GENERATE BRIEFS
# -----------------------------------

for investor_id, investor_rows in investors.items():

    first_name = investor_rows[0].FirstName
    last_name = investor_rows[0].LastName
    email = investor_rows[0].Email
    portfolio_name = investor_rows[0].PortfolioName

    company_news = defaultdict(list)

    for row in investor_rows:
        company_news[(row.Ticker, row.CompanyName, row.Sector)].append({
            "title": row.Title,
            "summary": row.Content or "",
            "source": row.Source,
            "published": row.PublishedAt,
            "sentiment": row.SentimentLabel or "not analyzed",
            "sentiment_score": row.SentimentScore,
            "relevance_score": row.RelevanceScore or 0,
            "relevance_method": row.RelevanceMethod or "unknown",
            "tfidf_similarity": row.TfidfSimilarity or 0,

            "trade_date": row.TradeDate,
            "last_price": row.LastPrice,
            "last_price_time": row.LastPriceTime,
            "open_price": row.OpenPrice,
            "high_price": row.HighPrice,
            "low_price": row.LowPrice,
            "close_price": row.ClosePrice,
            "volume": row.Volume
        })

    all_sentiments = [
        article["sentiment"]
        for articles in company_news.values()
        for article in articles
        if article["sentiment"] != "not analyzed"
    ]

    total_articles = sum(len(articles) for articles in company_news.values())
    portfolio_tone = get_portfolio_tone(all_sentiments)

    sector_exposure = calculate_sector_exposure(company_news)

    most_discussed = max(
        company_news.items(),
        key=lambda x: len(x[1])
    )

    most_discussed_ticker = most_discussed[0][0]
    most_discussed_count = len(most_discussed[1])

    company_positive_scores = {}
    company_negative_scores = {}

    for (ticker, company_name, sector), articles in company_news.items():

        positive_count = sum(
            1 for a in articles
            if a["sentiment"] == "positive"
        )

        negative_count = sum(
            1 for a in articles
            if a["sentiment"] == "negative"
        )

        company_positive_scores[ticker] = positive_count
        company_negative_scores[ticker] = negative_count

    strongest_positive = max(
        company_positive_scores,
        key=company_positive_scores.get
    )

    highest_negative = max(
        company_negative_scores,
        key=company_negative_scores.get
    )

    brief_lines = []

    brief_lines.append(f"Daily Investor Brief - {brief_date}")
    brief_lines.append("")
    brief_lines.append(f"Investor: {first_name} {last_name}")
    brief_lines.append(f"Portfolio: {portfolio_name}")
    brief_lines.append("")
    brief_lines.append("Executive summary")
    brief_lines.append("-" * 60)
    brief_lines.append(
        f"Today's brief covers {len(company_news)} portfolio companies "
        f"and {total_articles} relevant articles."
    )
    brief_lines.append(f"Overall portfolio news tone: {portfolio_tone}.")
    brief_lines.append(
        "The notes below focus on the most relevant company-specific updates "
        "detected in the latest news flow."
    )
    brief_lines.append("")

    # -----------------------------------
    # PORTFOLIO ANALYTICS
    # -----------------------------------

    brief_lines.append("Portfolio analytics")
    brief_lines.append("-" * 60)

    brief_lines.append(
        f"Portfolio company count: {len(company_news)}"
    )

    brief_lines.append("Sector exposure:")

    for sector_name, exposure in sector_exposure.items():

        brief_lines.append(
            f"- {sector_name}: {exposure}%"
        )

    brief_lines.append("")

    brief_lines.append(
        f"Most discussed holding: "
        f"{most_discussed_ticker} "
        f"({most_discussed_count} articles)"
    )

    brief_lines.append(
        f"Strongest positive sentiment: "
        f"{strongest_positive}"
    )

    brief_lines.append(
        f"Highest negative sentiment exposure: "
        f"{highest_negative}"
    )

    brief_lines.append("")    

    # -----------------------------------
    # SECTOR OVERVIEW
    # -----------------------------------

    sector_data = defaultdict(list)

    for (ticker, company_name, sector), articles in company_news.items():
        sector_name = sector or "Unknown"

        for article in articles:
            sector_data[sector_name].append(article)

    brief_lines.append("Sector overview")
    brief_lines.append("-" * 60)

    for sector_name, articles in sector_data.items():
        sentiments = [
            a["sentiment"]
            for a in articles
            if a["sentiment"] != "not analyzed"
        ]

        sector_tone = get_sector_tone(sentiments)

        brief_lines.append(
            f"{sector_name}: {sector_tone}, "
            f"{len(articles)} relevant article(s)"
        )

    brief_lines.append("")

    # -----------------------------------
    # COMPANY SECTIONS
    # -----------------------------------

    for (ticker, company_name, sector), articles in company_news.items():

        articles = sorted(
            articles,
            key=lambda x: (
                x["relevance_score"],
                x["tfidf_similarity"],
                x["sentiment_score"] or 0
            ),
            reverse=True
        )

        sentiments = [
            a["sentiment"]
            for a in articles
            if a["sentiment"] != "not analyzed"
        ]

        dominant_sentiment = get_dominant_sentiment(sentiments)
        sentiment_counts = Counter(sentiments)

        brief_lines.append(f"{ticker} - {company_name}")
        brief_lines.append("-" * 60)

        # -----------------------------------
        # MARKET SNAPSHOT
        # -----------------------------------

        market = articles[0]

        if market["last_price"] is not None:
            daily_move = format_daily_move(
            market["open_price"],
            market["close_price"]
        )

        brief_lines.append("Market snapshot:")
        brief_lines.append(
            f"Latest price: {format_price(market['last_price'])} "
            f"(as of {format_datetime(market['last_price_time'])} local system time)"
        )
        brief_lines.append("")
        brief_lines.append(f"Last completed session ({market['trade_date']}):")
        brief_lines.append(f"- Open: {format_price(market['open_price'])}")
        brief_lines.append(f"- High: {format_price(market['high_price'])}")
        brief_lines.append(f"- Low: {format_price(market['low_price'])}")
        brief_lines.append(f"- Close: {format_price(market['close_price'])}")
        brief_lines.append(f"- Daily move: {daily_move}")
        brief_lines.append(f"- Volume: {format_volume(market['volume'])}")
        brief_lines.append("")

        brief_lines.append(f"Relevant articles: {len(articles)}")
        brief_lines.append(f"Media tone: {dominant_sentiment}")

        if sentiment_counts:
            brief_lines.append(
                "Sentiment breakdown: "
                f"positive={sentiment_counts.get('positive', 0)}, "
                f"neutral={sentiment_counts.get('neutral', 0)}, "
                f"negative={sentiment_counts.get('negative', 0)}"
            )

        brief_lines.append("")
        brief_lines.append("Investor takeaway:")
        brief_lines.append(build_takeaway(ticker, dominant_sentiment, articles))
        brief_lines.append("")
        brief_lines.append("Key items:")

        for article in articles[:3]:
            score = article["sentiment_score"]

            if score is not None:
                sentiment_text = f"{article['sentiment']} ({score:.2f})"
            else:
                sentiment_text = article["sentiment"]

            brief_lines.append(
                f"- {article['title']} [{sentiment_text}]"
            )

        brief_lines.append("")

    brief_lines.append("")
    brief_lines.append("-" * 60)
    brief_lines.append(
        "Disclaimer: This brief is for informational purposes only "
        "and does not constitute investment advice."
    )

    brief_text = "\n".join(brief_lines)

    # -----------------------------------
    # DUPLICATE PROTECTION
    # -----------------------------------

    cursor.execute("""
        SELECT BriefID
        FROM DailyBriefs
        WHERE InvestorID = ?
          AND BriefDate = ?
    """, investor_id, brief_date)

    existing_brief = cursor.fetchone()

    if existing_brief:
        print(
            f"Brief already exists for InvestorID {investor_id} "
            f"on {brief_date}. Skipping."
        )
        continue

    cursor.execute("""
        INSERT INTO DailyBriefs
        (
            InvestorID,
            BriefDate,
            BriefText
        )
        VALUES (?, ?, ?)
    """,
    investor_id,
    brief_date,
    str(brief_text)
    )

    conn.commit()

    print(f"Brief v3 generated for {email}")

cursor.close()
conn.close()

print("Done.")