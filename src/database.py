from pathlib import Path
import sqlite3
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobsearch.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_titles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        job_title_id INTEGER,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        date_scraped TEXT,
        FOREIGN KEY(country_id) REFERENCES countries(id),
        FOREIGN KEY(job_title_id) REFERENCES job_titles(id)
    )
    """)
    conn.commit()
    conn.close()

def get_or_create(table, column, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    row = cur.fetchone()
    if row:
        id_ = row[0]
    else:
        cur.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
        conn.commit()
        id_ = cur.lastrowid
    conn.close()
    return id_

def insert_job(country_id, job_title_id, title, company, location, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO jobs (country_id, job_title_id, title, company, location, description, date_scraped)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (country_id, job_title_id, title, company, location, description, datetime.now().isoformat()))
    conn.commit()
    conn.close()
