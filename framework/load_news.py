import pyodbc
import yfinance as yf
from relevance_engine import calculate_relevance

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
# GET COMPANIES
# -----------------------------------

cursor.execute("""
    SELECT
        c.CompanyID,
        c.Ticker,
        c.CompanyName,
        ck.Keyword
    FROM Companies c
    LEFT JOIN CompanyKeywords ck
        ON c.CompanyID = ck.CompanyID
    ORDER BY c.Ticker
""")
company_rows = cursor.fetchall()

companies = {}

for row in company_rows:
    company_id = row.CompanyID

    if company_id not in companies:
        companies[company_id] = {
            "company_id": row.CompanyID,
            "ticker": row.Ticker,
            "company_name": row.CompanyName,
            "keywords": set()
        }

    if row.Keyword:
        companies[company_id]["keywords"].add(row.Keyword.lower())

# -----------------------------------
# LOAD NEWS
# -----------------------------------

for company in companies.values():

    company_id = company["company_id"]
    ticker = company["ticker"]
    company_name = company["company_name"]
    extra_keywords = company["keywords"]

    print(f"\nLoading news for {ticker}...")

    yf_ticker = yf.Ticker(ticker)

    try:
        news = yf_ticker.news

        for article in news[:5]:

            content = article.get("content", {})

            title = content.get("title")
            summary = content.get("summary")
            pub_date = content.get("pubDate")

            canonical_url = content.get("canonicalUrl", {})
            url = canonical_url.get("url")

            provider = content.get("provider", {})
            source = provider.get("displayName")

            relevance = calculate_relevance(
                ticker=ticker,
                company_name=company_name,
                title=title,
                summary=summary,
                extra_keywords=extra_keywords
            )

            if not relevance["is_relevant"]:
                print(f"Skipped irrelevant news: {title}")
                continue

            relevance_score = relevance["score"]
            relevance_method = relevance["method"]
            tfidf_similarity = relevance["tfidf_similarity"]

            if not title or not url:
                continue

            try:

                cursor.execute("""
                    INSERT INTO News
                    (
                        CompanyID,
                        PublishedAt,
                        Source,
                        Title,
                        Url,
                        Content,
                        RelevanceScore,
                        RelevanceMethod,
                        TfidFSimilarity
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                company_id,
                pub_date,
                source,
                title,
                url,
                summary,
                relevance_score,
                relevance_method,
                tfidf_similarity
                )

                conn.commit()

                print(f"Inserted: {title}")

            except Exception as e:
                print(f"Skipped duplicate or error: {e}")

    except Exception as e:
        print(f"Error for {ticker}: {e}")

# -----------------------------------
# CLOSE
# -----------------------------------

cursor.close()
conn.close()

print("\nDone.")