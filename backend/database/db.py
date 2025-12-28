import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with starred stocks and users tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Starred stocks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS starred_stocks (
            symbol TEXT PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_starred_stocks():
    """Get all starred stocks"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT symbol, added_at, last_updated FROM starred_stocks ORDER BY added_at DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]

def add_starred_stock(symbol):
    """Add a stock to starred list"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO starred_stocks (symbol, last_updated)
        VALUES (?, ?)
    ''', (symbol, datetime.now()))
    
    conn.commit()
    conn.close()

def remove_starred_stock(symbol):
    """Remove a stock from starred list"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM starred_stocks WHERE symbol = ?', (symbol,))
    
    conn.commit()
    conn.close()

def update_stock_timestamp(symbol):
    """Update last_updated timestamp for a stock"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE starred_stocks 
        SET last_updated = ? 
        WHERE symbol = ?
    ''', (datetime.now(), symbol))
    
    conn.commit()
    conn.close()

# User authentication functions
def create_user(email, password_hash):
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
        ''', (email.lower().strip(), password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Email already exists

def get_user_by_email(email):
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, password_hash, created_at, last_login FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def update_last_login(user_id):
    """Update last login timestamp"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET last_login = ? 
        WHERE id = ?
    ''', (datetime.now(), user_id))
    
    conn.commit()
    conn.close()

def get_user_count():
    """Get total number of registered users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    row = cursor.fetchone()
    conn.close()
    
    return row['count'] if row else 0

