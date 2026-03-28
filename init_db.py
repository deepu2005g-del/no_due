import os
import psycopg2
from dotenv import load_dotenv

# Load env from backend directory
env_path = os.path.join('backend', '.env')
load_dotenv(env_path)

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

print(f"Connecting to: {db_url}")

def run_sql_file(cursor, file_path):
    print(f"Executing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        cursor.execute(sql)

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Run schema first
    schema_path = os.path.join('backend', 'schema.sql')
    run_sql_file(cur, schema_path)
    
    # Run seed data
    seed_path = os.path.join('backend', 'seed_data.sql')
    run_sql_file(cur, seed_path)
    
    print("Database initialization successful!")
    
    # Verification
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
    tables = cur.fetchall()
    print("Tables created:")
    for table in tables:
        print(f" - {table[0]}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    exit(1)
