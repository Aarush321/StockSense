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
    
    # Starred stocks table (now user-specific)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS starred_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, symbol),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Add user_id column to existing starred_stocks table if it doesn't exist (migration)
    try:
        cursor.execute('ALTER TABLE starred_stocks ADD COLUMN user_id INTEGER')
        # Delete all old starred stocks since we can't associate them with users
        cursor.execute('DELETE FROM starred_stocks WHERE user_id IS NULL')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create index for faster lookups
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_starred_stocks_user_id ON starred_stocks(user_id)')
    except sqlite3.OperationalError:
        pass
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires TIMESTAMP,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Add new columns to existing table if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN verification_token TEXT')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN reset_token TEXT')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN name TEXT')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

def get_starred_stocks(user_id):
    """Get all starred stocks for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT symbol, added_at, last_updated 
        FROM starred_stocks 
        WHERE user_id = ?
        ORDER BY added_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]

def add_starred_stock(user_id, symbol):
    """Add a stock to starred list for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO starred_stocks (user_id, symbol, last_updated)
        VALUES (?, ?, ?)
    ''', (user_id, symbol, datetime.now()))
    
    conn.commit()
    conn.close()

def remove_starred_stock(user_id, symbol):
    """Remove a stock from starred list for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM starred_stocks WHERE user_id = ? AND symbol = ?', (user_id, symbol))
    
    conn.commit()
    conn.close()

def update_stock_timestamp(user_id, symbol):
    """Update last_updated timestamp for a stock"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE starred_stocks 
        SET last_updated = ? 
        WHERE user_id = ? AND symbol = ?
    ''', (datetime.now(), user_id, symbol))
    
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
    
    cursor.execute('SELECT id, email, password_hash, email_verified, verification_token, reset_token, reset_token_expires, name, created_at, last_login FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, password_hash, email_verified, verification_token, reset_token, reset_token_expires, name, created_at, last_login FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def update_user_verification_token(user_id, token):
    """Update verification token for user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET verification_token = ? WHERE id = ?', (token, user_id))
    conn.commit()
    conn.close()

def verify_user_email(user_id):
    """Mark user email as verified"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET email_verified = 1, verification_token = NULL WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_user_by_verification_token(token):
    """Get user by verification token"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, email_verified FROM users WHERE verification_token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def set_password_reset_token(email, token, expires_at):
    """Set password reset token for user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE email = ?', (token, expires_at, email.lower().strip()))
    conn.commit()
    conn.close()

def get_user_by_reset_token(token):
    """Get user by reset token"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, reset_token_expires FROM users WHERE reset_token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def reset_user_password(user_id, new_password_hash):
    """Reset user password and clear reset token"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL WHERE id = ?', (new_password_hash, user_id))
    conn.commit()
    conn.close()

def update_user_profile(user_id, name=None):
    """Update user profile information"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if name is not None:
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
    conn.commit()
    conn.close()

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

def get_all_users():
    """Get all registered users (for admin purposes)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, email, name, created_at, last_login, email_verified
        FROM users
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

