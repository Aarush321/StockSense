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
    """Initialize database with starred stocks table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS starred_stocks (
            symbol TEXT PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

