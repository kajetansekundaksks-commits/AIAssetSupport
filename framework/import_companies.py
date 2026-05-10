import pandas as pd
import pyodbc

CSV_PATH = "data/company_universe.csv"

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
    company_name = row["CompanyName"]
    exchange = row["Exchange"]
    country = row["Country"]
    sector = row["Sector"]

    cursor.execute("""
        SELECT CompanyID
        FROM Companies
        WHERE Ticker = ?
    """, ticker)

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE Companies
            SET
                CompanyName = ?,
                Exchange = ?,
                Country = ?,
                Sector = ?
            WHERE Ticker = ?
        """,
        company_name,
        exchange,
        country,
        sector,
        ticker
        )

        print(f"Updated: {ticker}")

    else:
        cursor.execute("""
            INSERT INTO Companies
            (
                Ticker,
                CompanyName,
                Exchange,
                Country,
                Sector
            )
            VALUES (?, ?, ?, ?, ?)
        """,
        ticker,
        company_name,
        exchange,
        country,
        sector
        )

        print(f"Inserted: {ticker}")

    conn.commit()

cursor.close()
conn.close()

print("Company import completed.")