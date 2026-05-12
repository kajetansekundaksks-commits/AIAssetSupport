import pandas as pd
import pyodbc

CSV_PATH = "data/company_aliases.csv"

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

df = pd.read_csv(CSV_PATH)

for _, row in df.iterrows():
    ticker = row["Ticker"]
    alias = str(row["Alias"]).lower().strip()

    cursor.execute("""
        SELECT CompanyID
        FROM Companies
        WHERE Ticker = ?
    """, ticker)

    company = cursor.fetchone()

    if not company:
        print(f"Skipped {ticker}: company not found")
        continue

    company_id = company.CompanyID

    cursor.execute("""
        SELECT KeywordID
        FROM CompanyKeywords
        WHERE CompanyID = ?
          AND LOWER(Keyword) = ?
    """, company_id, alias)

    existing = cursor.fetchone()

    if existing:
        print(f"Already exists: {ticker} -> {alias}")
        continue

    cursor.execute("""
        INSERT INTO CompanyKeywords
        (
            CompanyID,
            Keyword
        )
        VALUES (?, ?)
    """, company_id, alias)

    conn.commit()

    print(f"Inserted alias: {ticker} -> {alias}")

cursor.close()
conn.close()

print("Company aliases import completed.")