# SQLite Database Implementation for Victor

## Overview

The Victor bot detection system has been upgraded from JSON file storage to **SQLite database**. This ensures data persistence across runs and enables timeline-based analysis.

## What Changed

### Before (JSON-based)
- Traffic logs saved to `data/traffic_logs.json`
- File overwritten on each simulation run
- No historical data retention
- Limited querying capabilities

### After (SQLite-based)
- Traffic logs stored in `data/victor_traffic.db`
- All data persists automatically
- Multiple simulation runs accumulate data
- Advanced querying and timeline analysis
- Hourly aggregation for trends

## Database Schema

```sql
CREATE TABLE traffic_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    ip TEXT NOT NULL,
    user_agent TEXT,
    referer TEXT DEFAULT 'none',
    accept_lang TEXT DEFAULT 'none',
    path TEXT,
    method TEXT DEFAULT 'GET',
    status_code INTEGER,
    label INTEGER,                    -- 0 for human, 1 for bot
    session_id TEXT,                  -- UUID for each server session
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indices for fast queries
CREATE INDEX idx_timestamp ON traffic_logs(timestamp);
CREATE INDEX idx_ip ON traffic_logs(ip);
CREATE INDEX idx_session ON traffic_logs(session_id);
```

## Files Modified/Created

### New Files
- **`database.py`** - TrafficDatabase class for SQLite operations

### Updated Files
- **`honeypot.py`** - Flask server that logs to SQLite (was empty)
- **`feature_engineering.py`** - Reads from SQLite instead of JSON
- **`train_model.py`** - Updated error messages
- **`simulate_traffic.py`** - Updated log messages
- **`dashboard.py`** - New Timeline page + SQLite integration

## How to Use

### 1. Start the Honeypot Server
```bash
python honeypot.py
```
Output:
```
============================================================
  VICTOR HONEYPOT SERVER
============================================================
Starting honeypot server on http://127.0.0.1:5000
Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Available endpoints:
  GET /               - Homepage
  GET /articles       - Articles page
  GET /about          - About page
  GET /secret-data    - Honeypot endpoint
  GET /api/status     - Server status

Traffic is being logged to: data/victor_traffic.db

To start traffic simulation:
  1. Keep this server running (in background or separate terminal)
  2. Run: python simulate_traffic.py
============================================================
```

### 2. Run Traffic Simulation (New Terminal)
```bash
python simulate_traffic.py
```
- Simulates 40 human sessions
- Simulates 40 bot sessions
- All traffic logged to SQLite database

### 3. Extract Features
```bash
python feature_engineering.py
```
- Reads from SQLite `traffic_logs` table
- Creates `data/features.csv`
- Data persists - can be run multiple times

### 4. Train Models
```bash
python train_model.py
```
- Trains ensemble models
- Saves to `models/` folder

### 5. View Dashboard
```bash
streamlit run dashboard.py
```

## New Features

### Timeline Page
A brand-new dashboard page showing:
- **Hourly Traffic Volume** - Stacked area chart (Bots vs Humans)
- **Bot Detection Rate Trend** - Line chart showing % bots over time
- **Detailed Statistics** - Table with hourly breakdown
- **Insights Cards**:
  - Peak Hour (highest traffic)
  - Average Bot Rate
  - Average Requests Per Hour

### Database API

```python
from database import TrafficDatabase

db = TrafficDatabase()

# Get all logs
df = db.get_all_logs()

# Get logs for specific IP
ip_logs = db.get_logs_by_ip("192.168.1.1")

# Get logs by session
session_logs = db.get_logs_by_session("session-uuid")

# Get logs since timestamp
recent = db.get_logs_since("2024-05-21 10:00:00")

# Get hourly statistics (for timeline)
hourly_stats = db.get_timeline_stats()

# Get record count
total = db.get_record_count()

# Get unique IPs
unique_ips = db.get_unique_ips()

# Export to JSON
db.export_to_json("backup.json")

# Import from JSON
db.import_from_json("backup.json")

# Clear all data
db.clear_all()
```

## Running Multiple Simulations

You can now run multiple traffic simulations and the data will **accumulate**:

```bash
# First run
python honeypot.py &
python simulate_traffic.py
python feature_engineering.py
python train_model.py

# Second run - data persists!
python honeypot.py &
python simulate_traffic.py
python feature_engineering.py
python train_model.py

# Data from both runs is in the database
```

Each simulation gets a unique `session_id` so you can track which requests came from which run.

## Data Persistence

- Database file: `data/victor_traffic.db`
- All historical data is preserved
- No manual data management needed
- Automatic indices for fast queries

## Backwards Compatibility

If you have existing JSON data:
```python
from database import TrafficDatabase

db = TrafficDatabase()
db.import_from_json("data/traffic_logs.json")
```

## Performance

- SQLite is lightweight and serverless
- Suitable for millions of traffic records
- Indexed queries are very fast
- No external database required

## Troubleshooting

### Database locked error
Make sure only one process is writing to the database at a time.

### Data not appearing in dashboard
Run the full pipeline: `honeypot.py` → `simulate_traffic.py` → `feature_engineering.py` → `dashboard.py`

### Want to start fresh?
```python
from database import TrafficDatabase
db = TrafficDatabase()
db.clear_all()
```

Then restart the pipeline.
