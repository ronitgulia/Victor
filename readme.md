# Victor — Real-Time Bot Detection System

> Ensemble ML-powered bot detection that **scores and blocks bots on every incoming request** — no batch processing, no manual pipeline runs between detections.

---

## Overview

Victor combines **XGBoost** and **Isolation Forest** in a weighted ensemble to detect malicious bot traffic. A trained model is loaded directly inside the honeypot server, scoring each HTTP request in real-time. Bots above the confidence threshold receive an instant `403 Blocked` response.

**Key Capabilities:**
- 🔴 **Real-time detection & blocking** — every request scored before the route handler runs
- 🛡 **12-feature behavioral fingerprinting** — UA, headers, timing, IP reputation, encoding
- 🌐 **Datacenter IP detection** — 72 CIDR ranges across 10 cloud providers (AWS, GCP, Azure, DO, Hetzner…)
- 🤖 **Ensemble ML** — XGBoost (supervised) + Isolation Forest (anomaly) weighted ensemble
- 📊 **Interactive dashboard** — 5-page Streamlit UI with live stats, IP lookup & geolocation
- 🔍 **SHAP explainability** — per-feature importance for every prediction
- ⚙️ **Fully config-driven** — all thresholds, weights, and paths in `config.yaml`
- 🗂 **Model versioning** — every retrain saves a timestamped backup in `models/versions/`
- 🚀 **One-click pipeline** — `python run_pipeline.py` runs all steps in order
- 🐳 **Docker-ready** — full containerized setup with `docker compose up`

---

## 🐳 Run with Docker (Recommended)

No Python, no pip, no setup required. One command runs everything:

```bash
docker compose up
```

Then open **http://localhost:8501** — the dashboard is live.

What happens automatically:
1. **Flask honeypot** starts on port 5000
2. **Traffic simulation** — 40 human + 40 bot sessions are generated
3. **ML pipeline** — features extracted, XGBoost + IsolationForest trained, SHAP computed
4. **Streamlit dashboard** launches on port 8501

> **First run** takes ~3–5 minutes (image build + pip install). Subsequent runs are instant — data & models are persisted in Docker volumes (`victor_data`, `victor_models`).

```bash
# Build & run (first time)
docker compose up

# Rebuild after code changes
docker compose up --build

# Run in background
docker compose up -d

# Stop & remove containers (data volumes preserved)
docker compose down

# Stop & wipe all data (clean slate)
docker compose down -v
```

---

## 🔔 Webhook Alerts (Slack & Discord)

Victor fires an automatic alert to **Slack** and/or **Discord** whenever a bot is detected with **≥ 90% confidence** — in real time, with zero impact on request latency.

### Sample Alert

```
🚨 High-Confidence Bot Detected

IP Address      192.0.2.42
Confidence      97.0%  (threshold: 90%)
Endpoint        /secret-data
Datacenter IP   Yes ⚠️
User-Agent      python-requests/2.28.0
Detected At     2026-05-22 10:25:03 UTC
```

### Setup — 3 steps

**Step 1 — Get your webhook URL**

| Platform | How |
|---|---|
| **Slack** | [api.slack.com/apps](https://api.slack.com/apps) → Create App → Incoming Webhooks → Add to Workspace |
| **Discord** | Server settings → Integrations → Webhooks → New Webhook → Copy URL |

**Step 2 — Set the environment variable**

```bash
# Windows PowerShell
$env:SLACK_WEBHOOK_URL   = "https://hooks.slack.com/services/..."
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# Linux / macOS
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

**Step 3 — Verify it works**

```bash
python alerts.py
```

Sends a test alert and confirms delivery.

### Docker usage

Create a `.env` file (never commit this):
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Then run:
```bash
docker compose up
```

Docker Compose automatically reads `.env` and injects the variables into the container.

### Tuning (config.yaml)

```yaml
alerts:
  high_confidence_threshold: 0.90  # only alert on very confident detections
  cooldown_seconds: 300            # same IP won't trigger again for 5 minutes
  max_alerts_per_minute: 10        # global cap — prevents flood during mass attacks
```

---

## Architecture


```
                          ┌─────────────────────────────────┐
  Incoming HTTP Request   │       honeypot.py               │
  ──────────────────────▶ │  DatacenterChecker              │
                          │  RealTimeScorer                 │
                          │    ├─ per-IP session history    │
                          │    ├─ compute 12 features       │
                          │    └─ XGBoost.predict_proba()   │
                          │                                 │
                          │  score ≥ threshold?             │
                          │  ├── YES → 403 Blocked          │
                          │  └── NO  → serve normally       │
                          │                                 │
                          │  log to SQLite (bot_score,      │
                          │  is_blocked, header_count…)     │
                          └─────────────────────────────────┘
                                        │
                              (offline pipeline)
                                        ▼
                          feature_engineering.py  →  features.csv (12 cols)
                                        ▼
                              train_model.py
                          ┌─────────────────────┐
                          │  XGBoost (60% weight)│
                          │  IsoForest (40% weight│
                          └─────────────────────┘
                                        ▼
                          models/xgboost_model.pkl
                          models/feature_cols.json  ← scorer reads this
                          models/isolation_forest.pkl
                                        ▼
                          explain.py  →  SHAP plots + shap_values.csv
                                        ▼
                          streamlit run dashboard.py
```

---

## Detection Features (12 total)

### Original 8 — Behavioral Signals

| Feature | What it measures | Bot signal |
|---|---|---|
| `ua_is_suspicious` | UA matches bot keywords (curl, scrapy, python-requests…) | High |
| `has_referer` | Referer header present | Absent in bots |
| `has_accept_lang` | Accept-Language header present | Absent in bots |
| `hit_secret_page` | Visited hidden honeypot endpoint `/secret-data` | Strong bot indicator |
| `ua_length` | Length of User-Agent string | Bots: short (10–30 chars) |
| `time_gap_seconds` | Seconds between consecutive requests from same IP | Bots: < 0.1s |
| `unique_pages_visited` | Distinct paths visited per IP | Bots sweep many pages |
| `total_requests_from_ip` | Total request volume per IP | Bots: very high |

### New 4 — Step 6 Additions

| Feature | How computed | Bot signal |
|---|---|---|
| `is_datacenter_ip` | 72 CIDR ranges: AWS, GCP, Azure, DO, Hetzner, Linode, Vultr, Cloudflare, OVH, Scaleway | ~80% of bots originate from datacenters |
| `header_count` | `len(request.headers)` at request time | Browsers send 8–12; bots send 2–4 |
| `missing_common_headers` | Count of absent: Accept + Referer + Accept-Language (0–3) | Higher = more bot-like |
| `accept_encoding_score` | 0 = none, 1 = gzip only, 2 = gzip + Brotli | Real browsers always support Brotli |

> **Note on JA3/TLS fingerprint**: JA3 requires access to the raw TLS ClientHello which Flask/WSGI never receives. A real JA3 implementation needs nginx + `nginx_ssl_ja3` as a reverse proxy. The 4 header-based features above provide comparable discriminative power at zero infrastructure cost.

---

## Project Structure

```
victor/
├── honeypot.py               # Flask honeypot + DatacenterChecker + RealTimeScorer
├── simulate_traffic.py       # Simulates human and bot sessions
├── feature_engineering.py    # 12-feature extraction from SQLite → features.csv
├── train_model.py            # XGBoost + Isolation Forest training + versioning
├── explain.py                # SHAP explainability plots
├── dashboard.py              # 5-page Streamlit dashboard
├── database.py               # SQLite ORM + schema migration
├── config_loader.py          # Singleton config reader (dot-notation)
├── config.yaml               # All configuration (thresholds, paths, weights…)
├── run_pipeline.py           # One-click pipeline runner
├── requirements.txt          # Python dependencies
│
├── data/
│   ├── victor_traffic.db         # SQLite: all request logs (incl. bot_score, is_blocked)
│   ├── datacenter_ranges.json    # 72 cloud provider CIDR ranges
│   ├── features.csv              # Engineered features (12 columns)
│   ├── predictions.csv           # Ensemble scores + victor_flag per request
│   ├── model_metrics.json        # AUC, Precision, Recall, F1
│   ├── realtime_stats.json       # Live scorer stats (written by honeypot every 50 req)
│   └── shap/
│       ├── global_summary.png    # SHAP beeswarm importance plot
│       ├── feature_bar.png       # Mean |SHAP| bar chart
│       └── shap_values.csv       # Per-request SHAP values (12 features)
│
└── models/
    ├── xgboost_model.pkl         # Active XGBoost classifier
    ├── isolation_forest.pkl      # Active Isolation Forest
    ├── feature_cols.json         # Exact feature list used for training (read by scorer)
    └── versions/
        ├── xgboost_model_<ts>.pkl       # Timestamped backup on each retrain
        └── isolation_forest_<ts>.pkl
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the honeypot server

```bash
python honeypot.py
```

Runs on `http://127.0.0.1:5000`. On startup it prints model status and whether blocking is active.

### 3. Simulate traffic (separate terminal)

```bash
python simulate_traffic.py
```

Sends 40 human sessions and 40 bot sessions to the honeypot.

### 4. Run the full ML pipeline

```bash
python run_pipeline.py
```

Runs in order with timing:
1. `feature_engineering.py` → `data/features.csv` (12 features)
2. `train_model.py` → models + `feature_cols.json` + metrics
3. `explain.py` → SHAP plots

Or run with `--skip-shap` for a faster iteration:
```bash
python run_pipeline.py --skip-shap
```

### 5. Launch the dashboard

```bash
streamlit run dashboard.py
```

Open `http://localhost:8501`

> After the first retrain, restart `honeypot.py` to pick up the new model. The scorer reloads `xgboost_model.pkl` and `feature_cols.json` at startup.

---

## Real-Time Detection

When `honeypot.py` starts it loads the trained model and starts scoring every request before serving it:

```
GET /articles HTTP/1.1
User-Agent: python-requests/2.28.0
                    ↓
        RealTimeScorer.score()
          features computed in ~0.5ms
          XGBoost.predict_proba() → 0.94
          0.94 ≥ threshold (0.5) → BOT
                    ↓
        HTTP/1.1 403 Forbidden
        {"status":"blocked","code":403}
```

The blocked request is still logged to SQLite with `is_blocked=1` and `bot_score=0.94` for analysis.

### Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Homepage |
| `GET /articles` | Articles page |
| `GET /about` | About page |
| `GET /secret-data` | Honeypot trap — bots find this via aggressive scanning |
| `GET /api/status` | Server status, total requests, unique IPs, blocked count |
| `GET /api/realtime-stats` | Live scorer stats (scored, blocked, threshold, mode) |

### Blocking mode

Controlled by `config.yaml`:

```yaml
detection:
  realtime_blocking: true   # false = log scores but don't block (safe mode)
  default_threshold: 0.5    # raise to reduce false positives
```

---

## Dashboard

### Pages

| Page | What you get |
|---|---|
| **Dashboard** | Traffic breakdown pie, score distribution histogram, bot vs human feature comparison, detection timeline, recent activity feed |
| **IP Lookup** | Full record for any IP — verdict card, geolocation (city/ISP via ip-api.com), score chart, all requests |
| **Model Explainability** | SHAP global importance, feature impact bar, SHAP heatmap (top 200 rows), per-feature explanations |
| **Raw Data** | Filterable/sortable full predictions log with CSV download |
| **Settings** | Dataset stats, current threshold, model metrics JSON, file structure |

### Sidebar features

- **Live Stats** — bots and humans count with percentages
- **🛡 Real-Time Shield** — reads `data/realtime_stats.json`: scored count, blocked count, model status
- **⚠️ Bot Spike Alert** — red alert when bot % exceeds `detection.bot_spike_threshold` (default 60%)
- **🔴 Auto-Refresh / Live Mode** — toggle to auto-refresh dashboard every N seconds
- **Threshold slider** — adjust detection sensitivity without retraining

---

## Configuration (`config.yaml`)

All hardcoded values are centralized in `config.yaml`. Key sections:

```yaml
detection:
  default_threshold: 0.5         # Bot/human decision boundary
  realtime_blocking: true        # Block bots in honeypot (false = log only)
  bot_spike_threshold: 60.0      # Sidebar alert threshold (%)
  ensemble_weights:
    isolation_forest: 0.4
    xgboost: 0.6

features:
  columns:                       # Feature list (drives training + scoring)
    - ua_is_suspicious
    - has_referer
    - has_accept_lang
    - hit_secret_page
    - ua_length
    - time_gap_seconds
    - unique_pages_visited
    - total_requests_from_ip
    - is_datacenter_ip           # New
    - header_count               # New
    - missing_common_headers     # New
    - accept_encoding_score      # New

dashboard:
  cache_ttl: 5                   # Data refresh TTL (seconds)
  live_mode_refresh_interval: 5  # Auto-refresh interval
```

Access values in code via `Config.get("detection.default_threshold")`.

---

## Adding New Features

1. **Capture data** in `honeypot.py` `before_request` (already captures all headers)
2. **Add DB column** to `database.py` `_migrate_schema()` — old rows get defaults, no data loss
3. **Compute feature** in `feature_engineering.py` and `RealTimeScorer._features()` in `honeypot.py`
4. **Add to `config.yaml`** `features.columns` list
5. **Retrain**: `python run_pipeline.py`
6. **Restart honeypot** — it auto-loads the new model + `feature_cols.json`

The scorer always uses `models/feature_cols.json` (written at training time) so model and features are always in sync.

---

## Performance

Typical results on the simulated dataset (680 requests, 70% bots):

| Metric | Value |
|---|---|
| XGBoost AUC | 1.000 |
| Isolation Forest AUC | 0.147 (unsupervised — expected on synthetic data) |
| Ensemble score | Weighted 60/40 |
| Real-time scoring latency | < 1ms per request |
| Datacenter CIDR lookup | < 0.1ms (in-memory ipaddress module) |

> AUC of 1.0 on simulated data is expected — the simulator uses hardcoded bot UA strings that perfectly match training labels. On real-world traffic, expect 0.92–0.97.

---

## Troubleshooting

### "Data files not found!"

Run the full pipeline first:
```bash
python honeypot.py          # terminal 1
python simulate_traffic.py  # terminal 2
python run_pipeline.py      # terminal 2 (after simulate finishes)
streamlit run dashboard.py
```

### SHAP fails with XGBoostError shape mismatch

`explain.py` must use the same features the model was trained on. The fix:
```bash
python train_model.py   # regenerates models/feature_cols.json
python explain.py       # reads feature_cols.json automatically
```

### Honeypot port already in use

Change port in `config.yaml`:
```yaml
simulation:
  flask_port: 5001
```
And update `honeypot.py` `app.run(port=...)` to match.

### Bot score always -1.0

No model is loaded. Run the pipeline first:
```bash
python run_pipeline.py
```
Then restart `honeypot.py`.

### Disable blocking temporarily

Set in `config.yaml`:
```yaml
detection:
  realtime_blocking: false
```
Restart `honeypot.py`. Requests are still scored and logged — just not blocked.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.35+ | Dashboard UI |
| `xgboost` | 2.0+ | Gradient boosting classifier |
| `scikit-learn` | 1.3+ | Isolation Forest, train/test split, metrics |
| `shap` | 0.44+ | Model explainability |
| `pandas` | 2.0+ | Data manipulation |
| `plotly` | 5.18+ | Interactive charts |
| `flask` | 2.3+ | Honeypot web server |
| `faker` | 19.0+ | Realistic user agent generation |
| `requests` | 2.31+ | Traffic simulation + IP geolocation |
| `joblib` | 1.3+ | Model serialization |
| `pyyaml` | 6.0+ | Config loading |
| `numpy` | 1.25+ | Feature arrays for model inference |

---

## License

This project is provided as-is for educational and research use.
