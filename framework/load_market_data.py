import pyodbc
import yfinance as yf
from datetime import datetime

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

cursor.execute("""
    SELECT CompanyID, Ticker
    FROM Companies
    ORDER BY Ticker
""")

companies = cursor.fetchall()

for company in companies:
    company_id = company.CompanyID
    ticker = company.Ticker

    print(f"Loading market data for {ticker}...")

    try:
        yf_ticker = yf.Ticker(ticker)

        hist = yf_ticker.history(period="5d", interval="1d")

        if hist.empty:
            print(f"No historical data for {ticker}")
            continue

        last_session = hist.tail(1).iloc[0]
        trade_date = str(hist.tail(1).index[0].date())

        open_price = float(last_session["Open"])
        high_price = float(last_session["High"])
        low_price = float(last_session["Low"])
        close_price = float(last_session["Close"])
        volume = int(last_session["Volume"])

        fast_info = yf_ticker.fast_info

        last_price = None

        try:
            last_price_raw = fast_info.get("last_price")
            last_price = float(last_price_raw) if last_price_raw is not None else close_price
        except Exception:
            last_price = close_price

        last_price_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT MarketDataID
            FROM MarketData
            WHERE CompanyID = ?
              AND TradeDate = ?
        """, company_id, trade_date)

        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE MarketData
                SET
                    OpenPrice = ?,
                    HighPrice = ?,
                    LowPrice = ?,
                    ClosePrice = ?,
                    Volume = ?,
                    LastPrice = ?,
                    LastPriceTime = ?
                WHERE CompanyID = ?
                  AND TradeDate = ?
            """,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            last_price,
            last_price_time,
            company_id,
            trade_date
            )

            print(f"Updated market data for {ticker}")

        else:
            cursor.execute("""
                INSERT INTO MarketData
                (
                    CompanyID,
                    TradeDate,
                    OpenPrice,
                    HighPrice,
                    LowPrice,
                    ClosePrice,
                    Volume,
                    LastPrice,
                    LastPriceTime
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            company_id,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            last_price,
            last_price_time
            )

            print(f"Inserted market data for {ticker}")

        conn.commit()

    except Exception as e:
        print(f"Error loading market data for {ticker}: {e}")

cursor.close()
conn.close()

print("Market data loading completed.")