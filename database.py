"""
SQLite database module for Victor traffic logs.
Handles persistent storage of traffic data with timeline support.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

DB_PATH = "data/victor_traffic.db"


class TrafficDatabase:
    """SQLite database for traffic logs"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        Path("data").mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Traffic logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traffic_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    ip TEXT NOT NULL,
                    user_agent TEXT,
                    referer TEXT DEFAULT 'none',
                    accept_lang TEXT DEFAULT 'none',
                    path TEXT,
                    method TEXT DEFAULT 'GET',
                    status_code INTEGER,
                    label INTEGER,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for fast queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON traffic_logs(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ip ON traffic_logs(ip)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_session ON traffic_logs(session_id)"
            )
            
            conn.commit()
    
    def log_request(self, timestamp, ip, user_agent, referer, accept_lang, 
                   path, method="GET", status_code=200, label=None, session_id=None):
        """Log a single traffic request"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO traffic_logs 
                (timestamp, ip, user_agent, referer, accept_lang, path, method, status_code, label, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, ip, user_agent, referer or 'none', accept_lang or 'none', 
                  path, method, status_code, label, session_id))
            conn.commit()
    
    def log_requests_batch(self, records):
        """Log multiple traffic requests efficiently"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for record in records:
                cursor.execute("""
                    INSERT INTO traffic_logs 
                    (timestamp, ip, user_agent, referer, accept_lang, path, method, status_code, label, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get('timestamp'),
                    record.get('ip'),
                    record.get('user_agent'),
                    record.get('referer') or 'none',
                    record.get('accept_lang') or 'none',
                    record.get('path'),
                    record.get('method', 'GET'),
                    record.get('status_code', 200),
                    record.get('label'),
                    record.get('session_id')
                ))
            conn.commit()
    
    def get_all_logs(self):
        """Fetch all traffic logs as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM traffic_logs ORDER BY timestamp",
                conn
            )
        return df
    
    def get_logs_by_ip(self, ip):
        """Fetch logs for specific IP"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM traffic_logs WHERE ip = ? ORDER BY timestamp",
                conn,
                params=(ip,)
            )
        return df
    
    def get_logs_by_session(self, session_id):
        """Fetch logs for specific session"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM traffic_logs WHERE session_id = ? ORDER BY timestamp",
                conn,
                params=(session_id,)
            )
        return df
    
    def get_logs_since(self, timestamp):
        """Fetch logs since given timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM traffic_logs WHERE timestamp >= ? ORDER BY timestamp",
                conn,
                params=(timestamp,)
            )
        return df
    
    def get_timeline_stats(self):
        """Get hourly traffic statistics for timeline"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("""
                SELECT 
                    datetime(timestamp, 'start of hour') as hour,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) as bot_count,
                    SUM(CASE WHEN label = 0 THEN 1 ELSE 0 END) as human_count
                FROM traffic_logs
                GROUP BY datetime(timestamp, 'start of hour')
                ORDER BY hour
            """, conn)
        return df
    
    def get_unique_ips(self):
        """Get count of unique IPs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT ip) FROM traffic_logs")
            count = cursor.fetchone()[0]
        return count
    
    def get_record_count(self):
        """Get total number of traffic records"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM traffic_logs")
            count = cursor.fetchone()[0]
        return count
    
    def clear_all(self):
        """Clear all traffic logs (use with caution)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM traffic_logs")
            conn.commit()
    
    def export_to_json(self, output_file):
        """Export database to JSON file for compatibility"""
        df = self.get_all_logs()
        df.to_json(output_file, orient='records', default_handler=str)
    
    def import_from_json(self, json_file):
        """Import traffic logs from JSON file"""
        with open(json_file, 'r') as f:
            records = json.load(f)
        
        self.log_requests_batch(records)


if __name__ == "__main__":
    # Test database
    db = TrafficDatabase()
    print(f"✓ Database initialized at {db.db_path}")
    print(f"  Records: {db.get_record_count()}")
    print(f"  Unique IPs: {db.get_unique_ips()}")
