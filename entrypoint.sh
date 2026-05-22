#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# entrypoint.sh — Victor Bot Detection container startup
# ─────────────────────────────────────────────────────────────────
# Steps:
#   1. Start Flask honeypot server in background
#   2. Wait for Flask to be ready
#   3. Simulate traffic (bots + humans)
#   4. Run ML pipeline (features → training → SHAP)
#   5. Launch Streamlit dashboard in foreground
# ─────────────────────────────────────────────────────────────────
set -e

FLASK_PORT=${FLASK_PORT:-5000}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         ⚔  VICTOR — Bot Detection System  ⚔         ║"
echo "║                 Docker Container Boot                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Start Flask honeypot ─────────────────────────────────
echo "▶  [1/5] Starting Flask honeypot server on port $FLASK_PORT..."
python honeypot.py &
FLASK_PID=$!

# ── Step 2: Wait for Flask to be ready ───────────────────────────
echo "▶  [2/5] Waiting for Flask to be ready..."
for i in $(seq 1 20); do
    if curl -sf "http://127.0.0.1:$FLASK_PORT/" > /dev/null 2>&1; then
        echo "   ✓  Flask is up!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "   ✗  Flask did not start in time. Exiting."
        exit 1
    fi
    sleep 1
done

# ── Step 3: Simulate traffic ─────────────────────────────────────
echo "▶  [3/5] Simulating traffic (bots + humans)..."
python simulate_traffic.py
echo "   ✓  Traffic simulation complete."

# ── Step 4: Run ML pipeline ──────────────────────────────────────
echo "▶  [4/5] Running ML pipeline..."
python run_pipeline.py
echo "   ✓  Pipeline complete — models trained, SHAP values computed."

# ── Step 5: Launch Streamlit dashboard ───────────────────────────
echo ""
echo "▶  [5/5] Launching Streamlit dashboard..."
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   🚀  Dashboard ready at http://localhost:$STREAMLIT_PORT   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

exec streamlit run dashboard.py \
    --server.port "$STREAMLIT_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
