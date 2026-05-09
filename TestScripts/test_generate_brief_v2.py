import pyodbc
from datetime import date
from collections import defaultdict, Counter

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

investor_email = "examplemichaelscofield@example.com"
brief_date = str(date.today())

query = """
SELECT
    i.InvestorID,
    i.FirstName,
    i.LastName,
    i.Email,
    p.PortfolioName,
    c.Ticker,
    c.CompanyName,
    n.NewsID,
    n.Title,
    n.Content,
    n.Source,
    n.PublishedAt,
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
WHERE i.Email = ?
ORDER BY c.Ticker, n.PublishedAt DESC;
"""

cursor.execute(query, investor_email)
rows = cursor.fetchall()

if not rows:
    print("No data found for investor.")
    cursor.close()
    conn.close()
    raise SystemExit

investor_id = rows[0].InvestorID
first_name = rows[0].FirstName
last_name = rows[0].LastName
portfolio_name = rows[0].PortfolioName

company_news = defaultdict(list)

for row in rows:
    if row.NewsID is None:
        continue

    company_news[(row.Ticker, row.CompanyName)].append({
        "title": row.Title,
        "summary": row.Content or "",
        "source": row.Source,
        "published": row.PublishedAt,
        "sentiment": row.SentimentLabel or "not analyzed",
        "score": row.SentimentScore
    })

brief_lines = []

brief_lines.append(f"Daily Investor Brief - {brief_date}")
brief_lines.append("")
brief_lines.append(f"Investor: {first_name} {last_name}")
brief_lines.append(f"Portfolio: {portfolio_name}")
brief_lines.append("")
brief_lines.append("Executive summary")
brief_lines.append("-" * 60)

if not company_news:
    brief_lines.append("No relevant news found for the companies in this portfolio today.")
else:
    brief_lines.append(
        f"Relevant news was found for {len(company_news)} portfolio companies. "
        "The summaries below highlight recent media tone and key developments."
    )

brief_lines.append("")

for (ticker, company_name), articles in company_news.items():
    sentiments = [a["sentiment"] for a in articles if a["sentiment"] != "not analyzed"]
    sentiment_counts = Counter(sentiments)

    if sentiment_counts:
        dominant_sentiment = sentiment_counts.most_common(1)[0][0]
    else:
        dominant_sentiment = "not analyzed"

    article_count = len(articles)

    brief_lines.append(f"{ticker} - {company_name}")
    brief_lines.append("-" * 60)
    brief_lines.append(f"News volume: {article_count} relevant article(s)")
    brief_lines.append(f"Overall tone: {dominant_sentiment}")
    brief_lines.append("")

    if dominant_sentiment == "positive":
        brief_lines.append(
            "Interpretation: Recent coverage appears constructive. "
            "The company is currently receiving mostly favorable attention."
        )
    elif dominant_sentiment == "negative":
        brief_lines.append(
            "Interpretation: Recent coverage appears cautious or unfavorable. "
            "This company may require closer monitoring."
        )
    elif dominant_sentiment == "neutral":
        brief_lines.append(
            "Interpretation: Recent coverage appears mostly informational, "
            "without a clearly positive or negative tone."
        )
    else:
        brief_lines.append(
            "Interpretation: Sentiment has not been analyzed for these articles yet."
        )

    brief_lines.append("")
    brief_lines.append("Key items:")

    for article in articles[:3]:
        score = article["score"]
        if score is not None:
            sentiment_text = f"{article['sentiment']} ({score:.2f})"
        else:
            sentiment_text = article["sentiment"]

        brief_lines.append(f"- {article['title']} [{sentiment_text}]")

    brief_lines.append("")

brief_text = "\n".join(brief_lines)

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

cursor.close()
conn.close()

print("Brief v2 generated and saved.")
print("")
print(brief_text)