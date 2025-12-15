# backend/db.py
import os
from dotenv import load_dotenv
import pyodbc

# Load environment variables from .env file
load_dotenv()

def get_connection():
    """
    Returns a connection to the SQL Server database using SQL Server Authentication.
    Reads the following from .env:
        MSSQL_SERVER
        MSSQL_DATABASE
        MSSQL_USERNAME
        MSSQL_PASSWORD
    """
    # Read variables from .env
    server = os.getenv("MSSQL_SERVER", "localhost\\SQLEXPRESS")  # Replace with your instance if different
    database = os.getenv("MSSQL_DATABASE", "InsuranceDB")
    username = os.getenv("MSSQL_USERNAME")  # SQL Login, e.g., Vijay
    password = os.getenv("MSSQL_PASSWORD")  # SQL Login password

    if not username or not password:
        raise ValueError("MSSQL_USERNAME and MSSQL_PASSWORD must be set in .env for SQL Server Authentication")

    # Connection string using ODBC Driver 17
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )

    # Create and return the connection
    return pyodbc.connect(conn_str)
