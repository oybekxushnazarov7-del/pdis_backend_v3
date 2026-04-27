import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn