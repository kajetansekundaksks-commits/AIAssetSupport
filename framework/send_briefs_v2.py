import os
import pyodbc
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("GMAIL_APP_PASSWORD")

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
# GET UNSENT BRIEFS
# -----------------------------------

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
WHERE b.IsSent = 0
ORDER BY b.GeneratedAt DESC
"""

cursor.execute(query)

briefs = cursor.fetchall()

# -----------------------------------
# SEND EMAILS
# -----------------------------------

for brief in briefs:

    brief_id = brief.BriefID
    receiver_email = brief.Email

    subject = f"Daily Investor Brief - {brief.BriefDate}"

    body = brief.BriefText

    msg = MIMEText(body, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

            server.login(sender_email, app_password)

            server.send_message(msg)

        print(f"Email sent to {receiver_email}")

        # -----------------------------------
        # MARK AS SENT
        # -----------------------------------

        cursor.execute("""
            UPDATE DailyBriefs
            SET
                IsSent = 1,
                SentAt = GETDATE()
            WHERE BriefID = ?
        """, brief_id)

        conn.commit()

    except Exception as e:

        print(f"Failed sending email to {receiver_email}")
        print(e)

# -----------------------------------
# CLOSE
# -----------------------------------

cursor.close()
conn.close()

print("\nDone.")