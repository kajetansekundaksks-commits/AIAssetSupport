import pyodbc
from datetime import date

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

investor_email = "examplemichaelscofield@example.com"
brief_date = str(date.today())

# -----------------------------------
# GET INVESTOR DATA + NEWS + SENTIMENT
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
email = rows[0].Email
portfolio_name = rows[0].PortfolioName

# -----------------------------------
# BUILD BRIEF TEXT
# -----------------------------------

brief_lines = []

brief_lines.append(f"Daily Investor Brief - {brief_date}")
brief_lines.append("")
brief_lines.append(f"Investor: {first_name} {last_name}")
brief_lines.append(f"Email: {email}")
brief_lines.append(f"Portfolio: {portfolio_name}")
brief_lines.append("")
brief_lines.append("Portfolio news summary:")
brief_lines.append("")

current_ticker = None

for row in rows:
    if row.NewsID is None:
        continue

    if row.Ticker != current_ticker:
        current_ticker = row.Ticker
        brief_lines.append("")
        brief_lines.append(f"{row.Ticker} - {row.CompanyName}")
        brief_lines.append("-" * 60)

    sentiment_label = row.SentimentLabel or "not analyzed"
    sentiment_score = row.SentimentScore

    if sentiment_score is not None:
        sentiment_text = f"{sentiment_label} ({sentiment_score:.2f})"
    else:
        sentiment_text = sentiment_label

    brief_lines.append(f"Title: {row.Title}")
    brief_lines.append(f"Source: {row.Source}")
    brief_lines.append(f"Published: {row.PublishedAt}")
    brief_lines.append(f"Sentiment: {sentiment_text}")

    if row.Content:
        brief_lines.append(f"Summary: {row.Content[:300]}")

    brief_lines.append("")

brief_text = "\n".join(brief_lines)

# -----------------------------------
# SAVE TO DAILYBRIEFS
# -----------------------------------

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
brief_text
)

conn.commit()

cursor.close()
conn.close()

print("Brief generated and saved.")
print("")
print(brief_text)