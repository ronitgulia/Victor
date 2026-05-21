# Config Usage Guide for Victor

## Quick Start

### Import the config loader:
```python
from config_loader import Config, get_paths, get_features, get_models_config
```

### Usage Examples:

**In train_model.py:**
```python
from config_loader import Config, get_paths, get_features, get_models_config

# Load paths
paths = get_paths()
df = pd.read_csv(paths['features'])

# Get feature columns
features_config = get_features()
FEATURE_COLS = features_config['columns']

# Get model parameters
models_config = get_models_config()
iso_forest = IsolationForest(
    n_estimators=models_config['isolation_forest']['n_estimators'],
    contamination=models_config['isolation_forest']['contamination'],
    random_state=models_config['isolation_forest']['random_state']
)

xgb_model = XGBClassifier(
    n_estimators=models_config['xgboost']['n_estimators'],
    max_depth=models_config['xgboost']['max_depth'],
    learning_rate=models_config['xgboost']['learning_rate'],
    # ... rest of params
)
```

**In simulate_traffic.py:**
```python
from config_loader import get_simulation_config

sim_config = get_simulation_config()
BASE_URL = sim_config['base_url']
HUMAN_PAGES = sim_config['human']['pages']
BOT_PAGES = sim_config['bot']['pages']
human_sessions = sim_config['human']['num_sessions']
bot_sessions = sim_config['bot']['num_sessions']
```

**In feature_engineering.py:**
```python
from config_loader import Config

paths = Config.get_section('paths')
LOG_FILE = paths['traffic_logs']

features_config = Config.get_section('features')
BOT_KEYWORDS = features_config['bot_keywords']
```

**In dashboard.py:**
```python
from config_loader import Config

# Get all paths
paths = Config.get_section('paths')
preds = pd.read_csv(paths['predictions'])
features = pd.read_csv(paths['features'])

# Get detection settings
threshold = Config.get('detection.default_threshold')

# Get dashboard settings
cache_ttl = Config.get('dashboard.cache_ttl')
activity_feed_size = Config.get('dashboard.activity_feed_size')
```

## Key Benefits:

✅ **Single source of truth** — All settings in one place  
✅ **Easy to modify** — Change config.yaml, no code changes needed  
✅ **Type-safe** — Dot notation access with defaults  
✅ **Singleton pattern** — Loaded once, reused everywhere  
✅ **Flexible** — Use full keys or convenience functions  

## Available Config Sections:

- `paths` — All file paths
- `features` — Feature column names & bot keywords
- `models` — Model training parameters
- `detection` — Threshold & ensemble settings
- `simulation` — Traffic simulation parameters
- `dashboard` — Dashboard UI settings
- `shap` — SHAP explainability parameters
- `colors` — UI color definitions
- `performance` — Performance thresholds

## Testing the Config:

```bash
python config_loader.py
```

This will print all loaded configuration values.
