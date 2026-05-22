# SQLite Database Quick Start Guide

## Quick Start

### Step 1: Start Honeypot Server
Open Terminal 1:
```bash
python honeypot.py
```

### Step 2: Run Traffic Simulation
Open Terminal 2:
```bash
python simulate_traffic.py
```

### Step 3: Extract Features
```bash
python feature_engineering.py
```

### Step 4: Train Models
```bash
python train_model.py
```

### Step 5: View Dashboard
```bash
streamlit run dashboard.py
```

---

## New Timeline Page

The dashboard includes a **Timeline** page that shows:

✅ **Hourly Traffic Volume** — Number of requests per hour  
✅ **Bot Detection Rate** — Bot percentage over time  
✅ **Detailed Statistics** — Per-hour breakdown table  
✅ **Peak Hour** — The hour with the highest traffic volume  

---

## Database Features

### Data Persists Across Runs
```
First run:  100 requests → saved to database
Second run: 100 requests → appended to existing data
Total:      200 requests accumulated
```

### Multiple Session Tracking
Every time `honeypot.py` starts:
- A unique Session ID is generated
- All requests are tagged with that session ID
- The Timeline page shows data from all sessions combined

### IP-Based Analysis
```python
from database import TrafficDatabase

db = TrafficDatabase()

# Get all requests from a specific IP
ip_logs = db.get_logs_by_ip("192.168.1.1")

# Get all requests from a specific session
session_logs = db.get_logs_by_session("session-uuid")

# Get requests since a given timestamp
recent = db.get_logs_since("2024-05-21 10:00:00")

# Get hourly aggregated stats (used by the Timeline page)
hourly_stats = db.get_timeline_stats()
```

---

## File Structure

```
victor/
├── honeypot.py                 # Flask server — logs all traffic to SQLite
├── database.py                 # SQLite database helper class
├── simulate_traffic.py         # Simulates bot and human traffic
├── feature_engineering.py      # Extracts ML features from SQLite
├── train_model.py              # Trains XGBoost + Isolation Forest models
├── dashboard.py                # Streamlit dashboard (includes Timeline page)
│
└── data/
    ├── victor_traffic.db       # SQLite database — all traffic logs stored here
    ├── features.csv            # Engineered features with labels
    ├── predictions.csv         # Model predictions with ensemble scores
    ├── model_metrics.json      # AUC, Precision, Recall, F1 metrics
    └── shap/
        └── shap_values.csv

└── models/
    ├── isolation_forest.pkl
    └── xgboost_model.pkl
```

---

## Reset the Database (Start Fresh)

To wipe all data and start over:

```bash
python
```

Then in the Python REPL:
```python
from database import TrafficDatabase
db = TrafficDatabase()
db.clear_all()
exit()
```

All traffic records will be cleared. Re-run the full pipeline to generate new data.

---

## Important Notes

1. **SQLite is automatic** — Traffic is logged by `honeypot.py` directly into SQLite on every request
2. **Data is persistent** — Unlike JSON, the database is never overwritten between runs
3. **View the Timeline** — Open the dashboard and navigate to the "Timeline" page
4. **Run multiple simulations** — Each run adds to the existing dataset, increasing model accuracy

---

## Troubleshooting

❌ **"No data in Timeline"**  
Run all 4 steps in order: `honeypot.py` → `simulate_traffic.py` → `feature_engineering.py` → `train_model.py`

❌ **"Database locked error"**  
Ensure only one instance of `honeypot.py` is running at a time

❌ **"Empty features.csv"**  
Check whether the database contains traffic logs:
```python
from database import TrafficDatabase
db = TrafficDatabase()
print(f"Total records: {db.get_record_count()}")
print(f"Unique IPs: {db.get_unique_ips()}")
```

---

## More Information

See `SQLITE_SETUP.md` for the full database schema, API reference, and advanced usage.
