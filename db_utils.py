# db_utils.py
import psycopg2
import json
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'bugbounty',
    'user': 'postgres',
    'password': 'yourpassword',
    'host': '127.0.0.1',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def insert_or_update_program(platform, handle, name, data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO programs (platform, handle, name, data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (platform, handle)
                DO UPDATE SET name = EXCLUDED.name, data = EXCLUDED.data;
            """, (platform, handle, name, json.dumps(data)))

def get_program(platform, handle):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT data FROM programs WHERE platform = %s AND handle = %s", (platform, handle))
            row = cur.fetchone()
            return row['data'] if row else None

def get_all_handles(platform):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT handle FROM programs WHERE platform = %s", (platform,))
            return [row[0] for row in cur.fetchall()]

def delete_program(platform, handle):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM programs WHERE platform = %s AND handle = %s", (platform, handle))