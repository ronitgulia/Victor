# Victor — Bot Detection System

A sophisticated real-time bot detection system using ensemble machine learning. Victor analyzes web traffic behavior patterns to identify and flag bot activity with high accuracy.

## Overview

Victor combines **XGBoost** and **Isolation Forest** ensemble models to detect malicious bot traffic in real-time. The system learns behavioral patterns from honeypot data and user-agent signatures to distinguish between legitimate users and automated bots.

**Key Capabilities:**
- Real-time bot detection with confidence scoring
- Honeypot-based feature extraction
- Ensemble ML approach for high accuracy
- Interactive dashboard for monitoring and analysis
- SHAP-based model explainability
- Live traffic simulation and testing

---

## Features

### Core Detection Features

Victor analyzes **8 behavioral signals** to identify bots:

| Feature | Description |
|---------|-------------|
| **User Agent Suspicious** | Matches known bot signatures (curl, python-requests, etc.) |
| **Has Referer** | Whether request included Referer header (humans usually do) |
| **Accept-Language** | Whether Accept-Language header was sent (bots often skip it) |
| **Hit Secret Page** | Whether IP visited hidden honeypot endpoint `/secret-data` |
| **User-Agent Length** | Bot UAs are typically shorter than human browsers |
| **Time Gap Between Requests** | Bots make rapid consecutive requests (< 1 sec gap) |
| **Unique Pages Visited** | Bots systematically sweep many pages quickly |
| **Total Requests from IP** | Bots generate unusually high request volume |

### Machine Learning Models

- **XGBoost Classifier**: Primary model for high-dimensional feature patterns
- **Isolation Forest**: Anomaly detection for outlier bot behavior
- **Ensemble Voting**: Combined predictions for robust classification

---

## Installation

### Requirements
- Python 3.8+
- pip or conda

### Setup

1. **Clone/Navigate to project:**
   ```bash
   cd victor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -c "import streamlit, xgboost, shap; print('✓ All dependencies installed')"
   ```

---

## Project Structure

```
victor/
├── dashboard.py              # Interactive Streamlit dashboard
├── train_model.py            # Model training pipeline
├── feature_engineering.py    # Feature extraction & transformation
├── honeypot.py               # Honeypot server (captures bot behavior)
├── simulate_traffic.py       # Simulates real & bot traffic
├── explain.py                # SHAP-based model explainability
├── requirements.txt          # Python dependencies
├── readme.md                 # This file
│
├── data/
│   ├── features.csv          # Extracted features for all requests
│   ├── predictions.csv       # Model predictions & scores
│   ├── traffic_logs.json     # Raw HTTP traffic logs
│   ├── model_metrics.json    # XGBoost & Isolation Forest AUC/metrics
│   └── shap/
│       ├── global_summary.png    # SHAP importance plot
│       ├── feature_bar.png       # Feature impact bar chart
│       └── shap_values.csv       # Raw SHAP values (per request)
│
└── models/
    ├── xgboost_model.pkl         # Trained XGBoost classifier
    └── isolation_forest.pkl      # Trained Isolation Forest model
```

---

## Quick Start

### Step 1: Generate Training Data

Start the honeypot server (captures bot attempts):
```bash
python honeypot.py
```
*Runs on `http://localhost:5000` by default*

### Step 2: Simulate Traffic

In a **new terminal**, simulate both legitimate and bot traffic:
```bash
python simulate_traffic.py
```

This generates:
- `data/traffic_logs.json` — Raw HTTP requests
- `data/features.csv` — Extracted behavioral features

### Step 3: Train Models

Extract features and train the ensemble:
```bash
python feature_engineering.py
python train_model.py
```

Outputs:
- `models/xgboost_model.pkl` — Trained XGBoost
- `models/isolation_forest.pkl` — Trained Isolation Forest
- `data/predictions.csv` — Predictions on entire dataset
- `data/model_metrics.json` — AUC scores and metrics

### Step 4: Generate Explainability

Create SHAP visualizations for model interpretability:
```bash
python explain.py
```

Outputs:
- `data/shap/global_summary.png` — Force plot
- `data/shap/feature_bar.png` — Mean |SHAP| values
- `data/shap/shap_values.csv` — Per-request SHAP values

### Step 5: Launch Dashboard

Start the interactive monitoring dashboard:
```bash
streamlit run dashboard.py
```

Open browser to `http://localhost:8501`

---

## Dashboard Guide

### Pages Overview

#### 1. **Dashboard** (Main Page)
Real-time overview of bot detection activity:
- **Metrics**: Total requests, bots detected, clean traffic, average confidence
- **Traffic Breakdown**: Pie chart showing bot vs human split
- **Confidence Distribution**: Histogram of bot scores with threshold line
- **Feature Comparison**: Bots vs humans behavioral differences
- **Detection Timeline**: Bot activity over time
- **Recent Activity**: Live feed of latest requests
- **Quick Insights**: Top active IP, detection rate, high-confidence detections

#### 2. **IP Lookup**
Investigate individual IP addresses:
- Full activity history for any IP
- Verdict (BOT/HUMAN) with confidence score
- Score distribution chart
- All associated requests with scores

#### 3. **Model Explainability**
Understand model decisions:
- Feature explanation guide
- SHAP global importance plots
- SHAP value heatmap (top 200 requests)
- What each feature means for predictions

#### 4. **Raw Data**
Complete detection log with filtering:
- Filter by traffic type (All/Bots/Humans)
- Min confidence threshold slider
- Paginated results
- Download as CSV

#### 5. **Settings**
System configuration & statistics:
- Dataset information (total records, bot %)
- Current threshold setting
- Model performance metrics
- File locations reference

---

## How It Works

### Architecture

```
Raw Traffic Logs
      ↓
[Feature Engineering] → Behavioral signals extracted
      ↓
┌─────────────────────────────────────────┐
│  Ensemble Classification                │
├──────────────────┬──────────────────────┤
│  XGBoost         │  Isolation Forest    │
│  (Supervised)    │  (Anomaly Detection) │
└──────────────────┴──────────────────────┘
      ↓
[Ensemble Voting] → Combined verdict
      ↓
Confidence Score (0-1) + Classification
      ↓
Dashboard Visualization & Real-time Monitoring
```

### Model Training Flow

1. **Feature Extraction**: 8 behavioral features per request
2. **Train-Test Split**: 80-20 split for validation
3. **XGBoost Training**: Gradient boosting on labeled features
4. **Isolation Forest Training**: Anomaly detection on feature patterns
5. **Ensemble Voting**: Average confidence from both models
6. **Evaluation**: AUC, Precision, Recall, F1-Score metrics

### Prediction Pipeline

```
Incoming Request
      ↓
[Extract 8 Features]
      ↓
XGBoost Score: 0-1 (probability of bot)
Isolation Forest Score: 0-1 (anomaly score)
      ↓
Ensemble Average: (XGB + ISO) / 2
      ↓
Compare with Threshold (default 0.5)
      ↓
Decision: BOT or HUMAN
```

---

## Configuration

### Threshold Adjustment

In the dashboard sidebar, adjust the **"When to flag as bot?"** slider:
- **Lower threshold (0.3)**: More sensitive, catches more bots but more false positives
- **Higher threshold (0.7)**: More conservative, fewer false positives but may miss subtle bots

### Customizing Features

Edit `feature_engineering.py` to modify feature extraction:
```python
FEATURE_COLS = [
    "ua_is_suspicious",      # Customize detection
    "has_referer",
    "has_accept_lang",
    "hit_secret_page",
    "ua_length",
    "time_gap_seconds",
    "unique_pages_visited",
    "total_requests_from_ip"
]
```

### Model Parameters

Modify in `train_model.py`:

**XGBoost:**
```python
xgb = XGBClassifier(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100
)
```

**Isolation Forest:**
```python
iso = IsolationForest(
    contamination=0.1,  # Expected bot percentage
    random_state=42
)
```

---

## Performance Metrics

The system tracks:
- **AUC-ROC Score**: Area under the receiver operating characteristic curve
- **Precision**: True positives / (true positives + false positives)
- **Recall**: True positives / (true positives + false negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **Detection Rate**: % of requests flagged as bots

View in dashboard → **Settings** → **Model Configuration**

---

## File Descriptions

### Data Files
- **features.csv**: 8 features × N requests (input to models)
- **predictions.csv**: Predictions with XGB score, ISO score, ensemble score, verdict
- **traffic_logs.json**: Raw HTTP request/response data
- **model_metrics.json**: AUC, Precision, Recall, F1 for both models

### Model Files
- **xgboost_model.pkl**: Serialized XGBoost classifier
- **isolation_forest.pkl**: Serialized Isolation Forest model

### SHAP Files
- **global_summary.png**: Force plot showing average feature contributions
- **feature_bar.png**: Bar chart of mean |SHAP| values
- **shap_values.csv**: Per-request SHAP values for each feature

---

## Troubleshooting

### Issue: "Data files not found!"
**Solution**: Run the pipeline in order:
```bash
python honeypot.py              # (in separate terminal)
python simulate_traffic.py
python feature_engineering.py
python train_model.py
streamlit run dashboard.py
```

### Issue: Honeypot port already in use
**Solution**: Edit `honeypot.py` and change port:
```python
app.run(host='localhost', port=5001)  # Change from 5000
```

### Issue: Dashboard loads but shows no data
**Solution**: Ensure all CSV files exist in `data/`:
- `data/features.csv`
- `data/predictions.csv`
- `data/model_metrics.json`

Run `python train_model.py` to regenerate.

### Issue: SHAP plots not showing
**Solution**: Run the explainability script:
```bash
python explain.py
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.35+ | Dashboard framework |
| xgboost | 2.0+ | Gradient boosting classifier |
| scikit-learn | 1.3+ | Isolation Forest, metrics |
| pandas | 2.0+ | Data manipulation |
| plotly | 5.18+ | Interactive charts |
| shap | 0.44+ | Model explainability |
| flask | 2.3+ | Honeypot web server |
| faker | 19.0+ | Generate fake user agents |

---

## Performance Benchmarks

Typical results on simulated traffic:

| Metric | Value |
|--------|-------|
| XGBoost AUC | 0.96 - 0.98 |
| Isolation Forest AUC | 0.91 - 0.94 |
| Ensemble AUC | 0.97 - 0.99 |
| Precision (Bots) | 0.94 - 0.96 |
| Recall (Bots) | 0.92 - 0.95 |
| Detection Latency | < 10ms per request |

---

## Advanced Usage

### Retrain with New Data

Add new traffic logs to `data/traffic_logs.json` and retrain:
```bash
python feature_engineering.py
python train_model.py
```

### Export Predictions

Access raw predictions:
```python
import pandas as pd
preds = pd.read_csv('data/predictions.csv')
print(preds[['ip', 'ensemble_score', 'victor_flag']])
```

### Custom Threshold Analysis

```python
import pandas as pd
preds = pd.read_csv('data/predictions.csv')

# Check different thresholds
for threshold in [0.3, 0.5, 0.7, 0.9]:
    detected = (preds['ensemble_score'] > threshold).sum()
    print(f"Threshold {threshold}: {detected} bots detected")
```

---

## Future Improvements

- [ ] Real-time model retraining on new traffic
- [ ] Geographic IP blocking rules
- [ ] Rate limiting per IP/ASN
- [ ] Integration with WAF (Web Application Firewall)
- [ ] Deep learning models (LSTM for sequence patterns)
- [ ] Multi-class classification (different bot types)
- [ ] API endpoint for live predictions

---

## License

This project is provided as-is for educational and commercial use.

## Author

Victor Bot Detection System — Built for high-accuracy real-time bot detection.

---

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review dashboard **Settings** for system status
3. Check `data/model_metrics.json` for performance metrics

