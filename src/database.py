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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS search_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT,
        search_term TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS title_keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title_id INTEGER,
        keyword TEXT,
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

def get_search_params():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT country, search_term FROM search_params ORDER BY id LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None

def add_search_params(country, search_term):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO search_params (country, search_term) VALUES (?, ?)", (country, search_term))
    conn.commit()
    conn.close()

def add_keyword_for_title(job_title_id, keyword):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO title_keywords (job_title_id, keyword) VALUES (?, ?)", (job_title_id, keyword))
    conn.commit()
    conn.close()

def get_keywords_for_title(job_title_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT keyword FROM title_keywords WHERE job_title_id = ?", (job_title_id,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else []
