import pyodbc
from transformers import pipeline

# -----------------------------------
# FINBERT
# -----------------------------------

classifier = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

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
# GET NEWS WITHOUT SENTIMENT
# -----------------------------------

query = """
SELECT 
    n.NewsID,
    n.Title,
    n.Content
FROM News n
LEFT JOIN SentimentAnalysis s
    ON n.NewsID = s.NewsID
WHERE s.NewsID IS NULL
"""

cursor.execute(query)

news_list = cursor.fetchall()

# -----------------------------------
# ANALYZE
# -----------------------------------

for news in news_list:

    news_id = news.NewsID
    title = news.Title or ""
    content = news.Content or ""

    text = f"{title}. {content}"

    print(f"\nAnalyzing NewsID {news_id}")

    try:

        result = classifier(text[:512])[0]

        label = result["label"]
        score = float(result["score"])

        cursor.execute("""
            INSERT INTO SentimentAnalysis
            (
                NewsID,
                SentimentLabel,
                SentimentScore,
                ConfidenceScore,
                ModelName
            )
            VALUES (?, ?, ?, ?, ?)
        """,
        news_id,
        label,
        score,
        score,
        "FinBERT"
        )

        conn.commit()

        print(f"Inserted sentiment: {label} ({score:.4f})")

    except Exception as e:
        print(f"Error analyzing NewsID {news_id}: {e}")

# -----------------------------------
# CLOSE
# -----------------------------------

cursor.close()
conn.close()

print("\nDone.")