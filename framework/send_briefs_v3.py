import os
import pyodbc
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("GMAIL_APP_PASSWORD")

if not sender_email or not app_password:
    raise ValueError("Missing SENDER_EMAIL or GMAIL_APP_PASSWORD in .env")

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

query = """
SELECT
    b.BriefID,
    b.BriefDate,
    b.BriefText,
    i.Email,
    i.FirstName,
    i.LastName
FROM DailyBriefs b
JOIN Investors i
    ON b.InvestorID = i.InvestorID
WHERE NOT EXISTS (
    SELECT 1
    FROM EmailDeliveryLog e
    WHERE e.BriefID = b.BriefID
      AND e.DeliveryStatus = 'sent'
)
ORDER BY b.GeneratedAt DESC;
"""

cursor.execute(query)
briefs = cursor.fetchall()

if not briefs:
    print("No unsent briefs found.")

for brief in briefs:
    brief_id = brief.BriefID
    receiver_email = brief.Email

    subject = f"Daily Investor Brief - {brief.BriefDate}"

    msg = MIMEText(brief.BriefText, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    print(f"Trying to send BriefID {brief_id} to {receiver_email}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)

        cursor.execute("""
            INSERT INTO EmailDeliveryLog
            (
                BriefID,
                RecipientEmail,
                DeliveryStatus,
                ErrorMessage
            )
            VALUES (?, ?, ?, ?)
        """, brief_id, receiver_email, "sent", None)

        conn.commit()

        print(f"Email sent successfully to {receiver_email}")

    except Exception as e:
        error_message = str(e)

        cursor.execute("""
            INSERT INTO EmailDeliveryLog
            (
                BriefID,
                RecipientEmail,
                DeliveryStatus,
                ErrorMessage
            )
            VALUES (?, ?, ?, ?)
        """, brief_id, receiver_email, "failed", error_message)

        conn.commit()

        print(f"Failed sending email to {receiver_email}")
        print(error_message)

cursor.close()
conn.close()

print("Done.")