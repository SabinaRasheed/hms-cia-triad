import sqlite3
from datetime import datetime
from security import hash_password

DB_PATH = "hospital.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        diagnosis TEXT,
        anonymized_name TEXT,
        anonymized_contact TEXT,
        date_added TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        action TEXT,
        timestamp TEXT,
        details TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) as c FROM users")
    if cursor.fetchone()["c"] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin123'), 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('DrSahab', hash_password('doc123'), 'doctor'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('Sabina', hash_password('sabina123'), 'receptionist'))

    conn.commit()
    conn.close()

def log_action(user_id, role, action, details=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (user_id, role, action, timestamp, details) VALUES (?,?,?,?,?)",
        (user_id, role, action, datetime.utcnow().isoformat(), details)
    )
    conn.commit()
    conn.close()
