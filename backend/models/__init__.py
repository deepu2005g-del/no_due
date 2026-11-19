"""
Database connection helper.
Provides a context-managed connection to MySQL.
"""
import pymysql
import pymysql.cursors
import os
import re
from config import get_config

config = get_config()

DB_HOST = config.DB_HOST
DB_PORT = int(config.DB_PORT)
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_NAME = config.DB_NAME

def get_db():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, autocommit=True, cursorclass=pymysql.cursors.DictCursor
    )


def query_db(sql, params=None, one=False, commit=False):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Emulate RETURNING for MySQL
            returning_match = re.search(r'RETURNING\s+(.+)$', sql, re.IGNORECASE | re.DOTALL)
            returning_cols = returning_match.group(1).strip() if returning_match else None
            if returning_cols:
                sql = re.sub(r'\s+RETURNING\s+.+$', '', sql, flags=re.IGNORECASE | re.DOTALL)
            cur.execute(sql, params or ())
            if commit:
                conn.commit()
                last_id = cur.lastrowid
                if returning_cols and last_id:
                    # determine table
                    tmatch = re.search(r'(?:INSERT INTO|UPDATE)\s+(\w+)', sql, re.IGNORECASE)
                    table = tmatch.group(1) if tmatch else None
                    if table:
                        cur.execute(f"SELECT * FROM {table} WHERE id = %s", (last_id,))
                        row = cur.fetchone()
                        if one:
                            return row
                        return [row] if row else []
                if one:
                    return None
                return None
            # For SELECT/UPDATE without returning
            try:
                results = cur.fetchall()
            except Exception:
                results = None
            if one:
                return results[0] if results else None
            return results if results is not None else []
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise e
    finally:
        try:
            conn.close()
        except Exception:
            pass