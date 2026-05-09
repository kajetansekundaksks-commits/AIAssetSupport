import pyodbc
import pandas as pd

conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=CPTLAPTOP\SQLEXPRESS;"
    r"DATABASE=AIInvestorResearch;"
    r"Trusted_Connection=yes;"
)

query = "SELECT * FROM Companies"

df = pd.read_sql(query, conn)

print(df)