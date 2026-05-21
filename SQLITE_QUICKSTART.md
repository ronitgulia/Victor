# SQLite Database Quick Start Guide

## تیز ترین شروعات (Quick Start)

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

## نیا Timeline صفحہ (New Timeline Page)

Dashboard میں نیا **Timeline** page شامل ہے جو یہ دیکھاتا ہے:

✅ **Hourly Traffic Volume** - ہر گھنٹے میں کتنی requests آئیں
✅ **Bot Detection Rate** - بوٹس کا فیصد وقت کے ساتھ
✅ **Detailed Statistics** - ہر گھنٹے کی تفصیلات
✅ **Peak Hour** - سب سے زیادہ ٹریفک کب آیا

---

## ڈیٹابیس کی خصوصیات (Database Features)

### Data Persists
```
پہلا run: 100 requests → Database میں save ہو جاتے ہیں
دوسرا run: 100 requests → پہلے والے کے ساتھ add ہوتے ہیں
Final: 200 requests total
```

### Multiple Sessions Tracking
ہر بار جب honeypot.py چلاتے ہو:
- Unique Session ID بنتا ہے
- سب requests اسی session سے tag ہوتی ہیں
- Timeline میں سب sessions کا ڈیٹا نظر آتا ہے

### IP-based Analysis
```python
from database import TrafficDatabase

db = TrafficDatabase()

# کسی IP کے سب requests دیکھو
ip_logs = db.get_logs_by_ip("192.168.1.1")

# کسی session کے requests دیکھو
session_logs = db.get_logs_by_session("session-uuid")

# آخری گھنٹے کا ڈیٹا دیکھو
recent = db.get_logs_since("2024-05-21 10:00:00")

# ہر گھنٹے کی تفصیلات (Timeline کے لیے)
hourly_stats = db.get_timeline_stats()
```

---

## فائلوں کی بناوٹ (File Structure)

```
victor/
├── honeypot.py                 # Flask server (traffic logs کو SQLite میں save کرتا ہے)
├── database.py                 # SQLite database helper
├── simulate_traffic.py         # بوٹ اور انسان کی ٹریفک simulate کرتا ہے
├── feature_engineering.py      # SQLite سے features نکالتا ہے
├── train_model.py              # Models train کرتا ہے
├── dashboard.py                # Streamlit dashboard (اب Timeline page کے ساتھ)
│
└── data/
    ├── victor_traffic.db       # ✨ نیا SQLite database (تمام traffic یہاں ہے)
    ├── features.csv            # features (label کے ساتھ)
    ├── predictions.csv         # model predictions (ensemble scores)
    ├── model_metrics.json      # model کی performance metrics
    └── shap/
        └── shap_values.csv

└── models/
    ├── isolation_forest.pkl
    └── xgboost_model.pkl
```

---

## ڈیٹابیس سے شروع کریں (Reset Database)

اگر شروع سے آنا ہو:

```bash
# Python REPL کھول
python

# یہ commands چلا
from database import TrafficDatabase
db = TrafficDatabase()
db.clear_all()

# اب تمام data صاف ہو گیا
exit()
```

---

## اہم نکات (Important Notes)

1. **SQLite خودکار ہے** - Traffic logs خودکار طور پر honeypot.py سے SQLite میں جاتے ہیں
2. **ڈیٹا محفوظ رہتا ہے** - JSON کی طرح overwrite نہیں ہوتا
3. **Timeline دیکھنے کے لیے** - Dashboard کھولو اور "Timeline" پیج پر جاؤ
4. **Multiple runs کریں** - ہر run کا ڈیٹا add ہوتا ہے

---

## اگر مسائل ہوں (Troubleshooting)

❌ **"No data in Timeline"**
- سب 4 steps چلا: honeypot → simulate → feature_engineering → train_model

❌ **"Database locked error"**
- یقینی بناؤ کہ ایک وقت میں صرف ایک honeypot.py چل رہا ہے

❌ **"Empty features.csv"**
- SQLite میں traffic logs ہیں؟ Status check کرو:
  ```python
  from database import TrafficDatabase
  db = TrafficDatabase()
  print(f"Total records: {db.get_record_count()}")
  print(f"Unique IPs: {db.get_unique_ips()}")
  ```

---

## مزید معلومات (More Info)

مکمل تفصیل `SQLITE_SETUP.md` میں ہے۔
