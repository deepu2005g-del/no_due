import os
import psycopg2
from dotenv import load_dotenv

# Load env from backend directory
load_dotenv('./backend/.env')

db_url = os.getenv('DATABASE_URL')
print(f"Connecting to: {db_url}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
    tables = cur.fetchall()
    print("Tables found in database:")
    for table in tables:
        print(f" - {table[0]}")
    
    # Check if 'users' table has data
    if any(t[0] == 'users' for t in tables):
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        print(f"Number of users: {count}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
