# database.py
import sqlite3
import pandas as pd
import os

DB_PATH = "data/victor_traffic.db"

class TrafficDatabase:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT,
                ip          TEXT,
                user_agent  TEXT,
                referer     TEXT,
                accept_lang TEXT,
                path        TEXT,
                method      TEXT,
                status_code INTEGER,
                session_id  TEXT
            )
        """)
        self.conn.commit()

    def log_request(self, timestamp, ip, user_agent, referer,
                    accept_lang, path, method, status_code, session_id):
        self.conn.execute("""
            INSERT INTO traffic_logs
              (timestamp, ip, user_agent, referer, accept_lang,
               path, method, status_code, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, ip, user_agent, referer, accept_lang,
              path, method, status_code, session_id))
        self.conn.commit()

    def get_all_logs(self):
        """Returns all logs as a DataFrame with a label column."""
        df = pd.read_sql_query("SELECT * FROM traffic_logs", self.conn)
        if len(df) == 0:
            return df

        # Auto-label: bots = suspicious user agents OR hit secret page
        BOT_KEYWORDS = ["python", "scrapy", "curl", "go-http", "wget",
                        "bot", "crawl", "spider"]
        ua_is_bot = df["user_agent"].str.lower().apply(
            lambda ua: any(kw in ua for kw in BOT_KEYWORDS)
        )
        hit_secret = df["path"].str.contains("secret", na=False)
        df["label"] = ((ua_is_bot) | (hit_secret)).astype(int)
        return df

    def get_record_count(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM traffic_logs")
        return cur.fetchone()[0]

    def get_unique_ips(self):
        cur = self.conn.execute("SELECT COUNT(DISTINCT ip) FROM traffic_logs")
        return cur.fetchone()[0]

    def close(self):
        self.conn.close()