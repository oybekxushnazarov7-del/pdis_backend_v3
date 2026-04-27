import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres.ubatpburtsliyjrhbgyj:Xushnazarov%40123@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn