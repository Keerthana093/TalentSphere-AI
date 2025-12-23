import sqlite3
import hashlib
import pandas as pd

DB_NAME = "talentsphere_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users Table: Now explicitly stores company_name and company_type
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT, 
            role TEXT, 
            company_name TEXT, 
            company_type TEXT)''')
    
    # Scans Table
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_name TEXT, 
            job_role TEXT, 
            score REAL, 
            filename TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create Default Admin
    default_user = "admin"
    default_pass = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                  (default_user, default_pass, "Recruiter", "TechGlobal", "MNC"))
    except sqlite3.IntegrityError:
        pass 
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    
    # We fetch Company details here so we can use them in the Dashboard
    c.execute("SELECT role, company_name, company_type FROM users WHERE username=? AND password=?", (username, hashed_pass))
    result = c.fetchone()
    conn.close()
    
    if result: 
        return {
            "role": result[0], 
            "company_name": result[1] if result[1] else "General", 
            "company_type": result[2] if result[2] else "General"
        }
    return None

def add_user(username, password, role, company_name=None, company_type=None):
    if not username or not password: return False
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (username, hashed_pass, role, company_name, company_type))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def save_scan_result(username, job_role, score, filename):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scans (user_name, job_role, score, filename) VALUES (?, ?, ?, ?)", (username, job_role, score, filename))
    conn.commit()
    conn.close()

init_db()