"""
Database connection helper.
Provides a context-managed connection to PostgreSQL.
"""
import psycopg2
import psycopg2.extras
from config import get_config

from psycopg2 import pool

config = get_config()

# Initialize a global thread-safe connection pool
# Global connection to bypass all Supabase rate limits/deadlocks
global_conn = None

def get_db():
    global global_conn
    if global_conn is None or global_conn.closed:
        global_conn = psycopg2.connect(config.DATABASE_URL)
        global_conn.autocommit = True
    return global_conn




def query_db(sql, params=None, one=False, commit=False):
    """
    Execute a SQL query and return results as list of dicts.
    - one=True returns single row or None
    - commit=True commits the transaction (for INSERT/UPDATE/DELETE)
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            if commit:
                conn.commit()
                # For INSERT ... RETURNING, try to fetch results
                try:
                    results = cur.fetchall()
                    return dict(results[0]) if one and results else [dict(r) for r in results]
                except psycopg2.ProgrammingError:
                    return None
            results = cur.fetchall()
            if one:
                return dict(results[0]) if results else None
            return [dict(r) for r in results]
    except Exception as e:
        conn.rollback()
        raise e
