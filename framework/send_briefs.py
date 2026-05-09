import os
import pyodbc
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("GMAIL_APP_PASSWORD")

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

cursor.execute("""
SELECT 
    b.BriefID,
    i.Email,
    i.FirstName,
    i.LastName,
    b.BriefDate,
    b.BriefText
FROM DailyBriefs b
JOIN Investors i
    ON b.InvestorID = i.InvestorID
WHERE b.IsSent = 0
ORDER BY b.GeneratedAt DESC;
""")

briefs = cursor.fetchall()

for brief in briefs:
    subject = f"Daily Investor Brief - {brief.BriefDate}"

    msg = MIMEText(brief.BriefText, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = brief.Email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

    cursor.execute("""
        UPDATE DailyBriefs
        SET IsSent = 1,
            SentAt = GETDATE()
        WHERE BriefID = ?
    """, brief.BriefID)

    conn.commit()

    print(f"Sent brief to {brief.Email}")

cursor.close()
conn.close()

print("Done.")