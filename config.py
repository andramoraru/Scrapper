import pyodbc

def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-ANDRA;"  
        "DATABASE=ProductTracker;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)
