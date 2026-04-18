import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=PDIS;"
        "Trusted_Connection=yes;"
    )
    return conn 