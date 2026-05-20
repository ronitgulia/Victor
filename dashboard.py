import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os

st.set_page_config(
    page_title = "Victor — Bot Detection",
    page_icon  = "🛡️",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown("""
<style>
  * { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif !important; }

  /* ── global background ── */
  .stApp {
      background: #ffffff;
      color: #1f2937;
  }

  /* ── sidebar ── */
  [data-testid="stSidebar"] {
      background: #f8f9fa;
      border-right: 1px solid #e5e7eb;
  }

  /* ── metric cards ── */
  [data-testid="stMetric"] {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  [data-testid="stMetric"]:hover {
      border-color: #d1d5db;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  [data-testid="stMetricLabel"]  { color: #6b7280 !important; font-size: 0.75rem !important; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
  [data-testid="stMetricValue"]  { color: #111827 !important; font-size: 2rem !important; font-weight: 700; }
  [data-testid="stMetricDelta"]  { font-size: 0.85rem !important; font-weight: 500; }

  /* ── section headings ── */
  h1 { color: #111827 !important; font-weight: 700 !important; font-size: 2.2rem !important; }
  h2 { color: #1f2937 !important; font-weight: 600 !important; font-size: 1.4rem !important; }
  h3 { color: #374151 !important; font-weight: 600 !important; }

  /* ── divider ── */
  hr { border-color: #e5e7eb !important; }

  /* ── data table wrapper ── */
  .victor-table-wrap {
      overflow-x: auto;
      border-radius: 10px;
      border: 1px solid #e5e7eb;
      background: #ffffff;
      margin-top: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .victor-table-wrap table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
  }
  .victor-table-wrap th {
      background: #f3f4f6;
      color: #374151;
      padding: 12px 16px;
      text-align: left;
      font-weight: 600;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      border-bottom: 1px solid #e5e7eb;
  }
  .victor-table-wrap td {
      padding: 12px 16px;
      border-bottom: 1px solid #f3f4f6;
      color: #4b5563;
  }
  .victor-table-wrap tr:hover td { background: #f9fafb; }

  /* ── status badges ── */
  .badge-bot   { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca;
                 padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.75rem; }
  .badge-human { background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0;
                 padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.75rem; }

  /* ── radio + selectbox ── */
  .stRadio label, .stSelectbox label { color: #374151 !important; font-weight: 500; }

  /* ── info box ── */
  .info-card {
      background: #f0f4ff;
      border: 1px solid #d1d5f8;
      border-radius: 10px;
      padding: 18px 20px;
      margin-bottom: 16px;
  }
  .info-card b { color: #1e40af; }

  /* ── plotly charts ── */
  .js-plotly-plot { border-radius: 10px; overflow: hidden; }

  /* ── input fields ── */
  .stTextInput input, .stSlider [data-testid="stNumberInput"] {
      border: 1px solid #d1d5db !important;
      border-radius: 8px !important;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PLOTLY shared light layout
# ─────────────────────────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor = "#ffffff",
    plot_bgcolor  = "#f9fafb",
    font          = dict(color="#374151", family="system-ui, -apple-system, sans-serif"),
    xaxis         = dict(gridcolor="#e5e7eb", zerolinecolor="#e5e7eb"),
    yaxis         = dict(gridcolor="#e5e7eb", zerolinecolor="#e5e7eb"),
    legend        = dict(bgcolor="#ffffff", font=dict(color="#4b5563"), bordercolor="#e5e7eb", borderwidth=1),
    margin        = dict(t=30, b=40, l=10, r=10),
)

@st.cache_data
def load_data():
    preds    = pd.read_csv("data/predictions.csv")
    features = pd.read_csv("data/features.csv")
    return preds, features

@st.cache_data
def load_metrics():
    if os.path.exists("data/model_metrics.json"):
        with open("data/model_metrics.json") as f:
            return json.load(f)
    return None

@st.cache_data
def load_shap_csv():
    path = "data/shap/shap_values.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


FEATURE_COLS = [
    "ua_is_suspicious", "has_referer", "has_accept_lang",
    "hit_secret_page",  "ua_length",   "time_gap_seconds",
    "unique_pages_visited", "total_requests_from_ip"
]

preds, features = load_data()
metrics = load_metrics()


with st.sidebar:
    st.markdown("<div style='padding:16px 0'><h2 style='margin:0;color:#111827'>Victor</h2><p style='color:#6b7280;font-size:0.9rem;margin:4px 0'>Bot Detection</p></div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<span style='font-weight:600;color:#374151'>Navigation</span>", unsafe_allow_html=True)
    page = st.radio("", ["Dashboard", "IP Lookup", "Model Explainability", "Raw Data"], label_visibility="collapsed")
    st.divider()

    # model metrics in sidebar if available
    if metrics:
        st.markdown("<span style='font-weight:600;color:#374151'>Model Performance</span>", unsafe_allow_html=True)
        st.metric("XGBoost AUC", f"{metrics.get('xgb_auc', 0):.3f}")
        st.metric("Isolation Forest AUC", f"{metrics.get('iso_auc', 0):.3f}")
        st.divider()

    threshold = st.slider("Bot Score Threshold", 0.1, 0.9, 0.5, 0.05,
                          help="Requests above this score are flagged as bots")
    st.divider()

    total         = len(preds)
    flagged_bots  = int((preds["ensemble_score"] > threshold).sum())
    clean_humans  = total - flagged_bots

    st.markdown(f"""
    <div class='info-card'>
      <div style='font-weight:600;color:#1e40af;margin-bottom:8px'>Session Summary</div>
      <div style='font-size:0.85rem;color:#6b7280;margin-bottom:2px'>Total Requests</div>
      <div style='font-size:1.8rem;font-weight:700;color:#111827;margin-bottom:12px'>{total:,}</div>
      <div style='font-size:0.85rem;color:#dc2626;margin-bottom:2px'>• Flagged as Bots</div>
      <div style='font-size:1.5rem;font-weight:700;color:#dc2626;margin-bottom:12px'>{flagged_bots:,}</div>
      <div style='font-size:0.85rem;color:#16a34a;margin-bottom:2px'>• Clean (Human)</div>
      <div style='font-size:1.5rem;font-weight:700;color:#16a34a'>{clean_humans:,}</div>
    </div>
    """, unsafe_allow_html=True)


if page == "Dashboard":
    st.markdown("# Victor — Bot Detection Dashboard")
    st.markdown("<p style='color:#6b7280;margin-top:-12px;font-size:1rem'>Real-time behavioral fingerprinting with ensemble machine learning</p>", unsafe_allow_html=True)
    st.divider()

    avg_bot_score = round(preds["ensemble_score"].mean(), 3)
    c1.metric("Total Requests",  f"{total:,}")
    c2.metric("Bots Flagged",    f"{flagged_bots:,}",  delta=f"{bot_pct:.1f}%",   delta_color="inverse")
    c3.metric("Clean (Human)",   f"{clean_humans:,}",  delta=f"{human_pct:.1f}%")
    c4.metric("Avg Bot Score",   avg_bot_score,         delta="threshold 0.5",     delta_color="off")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Traffic Breakdown")
        pie_df = pd.DataFrame({"Type": ["Bot", "Human"], "Count": [flagged_bots, clean_humans]})
        fig_pie = px.pie(pie_df, names="Type", values="Count",
                         color="Type",
                         color_discrete_map={"Bot": "#dc2626", "Human": "#16a34a"},
                         hole=0.5)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                              marker=dict(line=dict(color="#ffffff", width=3)))
        fig_pie.update_layout(**CHART_LAYOUT)
        fig_pie.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    with right:
        st.subheader("Bot Confidence Score Distribution")
        fig_hist = px.histogram(preds, x="ensemble_score", nbins=35,
                                color_discrete_sequence=["#3b82f6"],
                                labels={"ensemble_score": "Bot Probability"})
        fig_hist.add_vline(x=threshold, line_dash="dash", line_color="#dc2626",
                           annotation_text=f"Threshold ({threshold})",
                           annotation_font_color="#dc2626")
        fig_hist.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    st.subheader("Feature Comparison — Bots vs Humans")

    bot_means   = features[features["label"] == 1][FEATURE_COLS].mean()
    human_means = features[features["label"] == 0][FEATURE_COLS].mean()
    compare_df  = pd.DataFrame({
        "Feature": FEATURE_COLS,
        "Bot":     bot_means.values,
        "Human":   human_means.values
    })

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Bot",   x=compare_df["Feature"], y=compare_df["Bot"],
                             marker_color="#dc2626", marker_opacity=0.85))
    fig_bar.add_trace(go.Bar(name="Human", x=compare_df["Feature"], y=compare_df["Human"],
                             marker_color="#16a34a", marker_opacity=0.85))
    fig_bar.update_layout(barmode="group", xaxis_tickangle=-20, **CHART_LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── row 3: score over time (if timestamp available) ──
        st.divider()
        st.subheader("Bot Score Over Time")
        preds_t = preds.copy()
        preds_t["timestamp"] = pd.to_datetime(preds_t["timestamp"], errors="coerce")
        preds_t = preds_t.dropna(subset=["timestamp"]).sort_values("timestamp")
        fig_line = px.line(preds_t, x="timestamp", y="ensemble_score",
                           color_discrete_sequence=["#3b82f6"])
        fig_line.add_hline(y=threshold, line_dash="dash", line_color="#dc2626")
        fig_line.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_line, use_container_width=True)


elif page == "IP Lookup":
    st.markdown("# IP Lookup")
    st.markdown("<p style='color:#6b7280;margin-top:-12px;font-size:1rem'>Check any IP address against the logged traffic data</p>", unsafe_allow_html=True)
    ip_input = st.text_input("Enter an IP address to inspect", placeholder="e.g. 127.0.0.1")

    if ip_input:
        ip_rows = preds[features["label"].index.isin(
            features[preds.index].index  # align on same index
        )].copy() if "ip" not in preds.columns else preds[preds.get("ip", pd.Series()) == ip_input]

        # fallback: search in features if ip column exists there
        feat_ip = features[features["ip"] == ip_input] if "ip" in features.columns else pd.DataFrame()
        pred_ip = preds.loc[feat_ip.index] if len(feat_ip) > 0 else pd.DataFrame()

        if len(pred_ip) == 0 and "ip" in preds.columns:
            pred_ip = preds[preds["ip"] == ip_input]

        if len(pred_ip) == 0:
            st.warning(f"No traffic records found for **{ip_input}**.")
        else:
            avg_score = pred_ip["ensemble_score"].mean()
            is_bot    = avg_score > threshold

            verdict_color = "#dc2626" if is_bot else "#16a34a"
            verdict_label = "BOT" if is_bot else "HUMAN"
            verdict_bg = "#fee2e2" if is_bot else "#dcfce7"
            verdict_border = "#fecaca" if is_bot else "#bbf7d0"

            st.markdown(f"""
            <div style='background:{verdict_bg};border:2px solid {verdict_border};
                        border-radius:12px;padding:24px;margin-bottom:20px'>
              <h3 style='color:{verdict_color};margin:0;font-size:1.5rem'>{verdict_label}</h3>
              <p style='color:#374151;margin:8px 0 0;font-size:0.95rem'>IP: <b>{ip_input}</b>
                 &nbsp;·&nbsp; {len(pred_ip)} requests logged
                 &nbsp;·&nbsp; Avg score: <b style='color:{verdict_color}'>{avg_score:.3f}</b>
              </p>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Requests",     len(pred_ip))
            col_b.metric("Avg Bot Score", f"{avg_score:.3f}")
            col_c.metric("Verdict",       "BOT" if is_bot else "HUMAN")

            st.markdown("**Score distribution for this IP**")
            fig_ip = px.histogram(pred_ip, x="ensemble_score", nbins=15,
                                  color_discrete_sequence=["#3b82f6"])
            fig_ip.add_vline(x=threshold, line_dash="dash", line_color="#dc2626")
            fig_ip.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_ip, use_container_width=True)
    else:
        st.info("💡 Enter an IP address above to see its full activity profile.")


# ─────────────────────────────────────────────────────────────────
# ── PAGE 3: MODEL EXPLAINABILITY ──
# ─────────────────────────────────────────────────────────────────

elif page == "Model Explainability":
    st.markdown("# Model Explainability")
    st.markdown("<p style='color:#6b7280;margin-top:-12px;font-size:1rem'>Understanding what drives bot detection predictions</p>", unsafe_allow_html=True)
    st.divider()

    shap_img_bar    = "data/shap/feature_bar.png"
    shap_img_global = "data/shap/global_summary.png"
    shap_csv        = load_shap_csv()

    if os.path.exists(shap_img_global) or os.path.exists(shap_img_bar):
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(shap_img_global):
                st.subheader("Global Feature Importance")
                st.image(shap_img_global, use_container_width=True)
        with col2:
            if os.path.exists(shap_img_bar):
                st.subheader("Average Feature Impact")
                st.image(shap_img_bar, use_container_width=True)
    else:
        st.warning("SHAP plots not found. Run `python explain.py` to generate them.")

    if shap_csv is not None:
        st.divider()
        st.subheader("SHAP Value Heatmap (top 200 rows)")
        shap_display = shap_csv.head(200)
        shap_renamed = shap_display.rename(columns={c: c.replace("shap_", "") for c in shap_display.columns})
        fig_heat = px.imshow(
            shap_renamed.values.T,
            x=list(range(len(shap_renamed))),
            y=list(shap_renamed.columns),
            color_continuous_scale="RdBu_r",
            aspect="auto",
            labels=dict(x="Request Index", y="Feature", color="SHAP")
        )
        fig_heat.update_layout(**CHART_LAYOUT, height=380)
        st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.subheader("What Each Feature Means")
        "ua_is_suspicious":      "User agent matches known bot signatures (python-requests, curl, etc.)",
        "has_referer":           "Whether the request came with a Referer header (humans usually do)",
        "has_accept_lang":       "Whether Accept-Language header was sent (bots often skip it)",
        "hit_secret_page":       "Whether the IP visited the hidden honeypot endpoint /secret-data",
        "ua_length":             "Length of the user agent string (bots tend to have shorter ones)",
        "time_gap_seconds":      "Seconds between requests from the same IP (bots move very fast)",
        "unique_pages_visited":  "Number of distinct pages visited (bots sweep many pages)",
        "total_requests_from_ip":"Total request count from this IP in the dataset",
    }
    for feat, desc in explanations.items():
        st.markdown(f"**`{feat}`** — {desc}")


elif page == "Raw Data":
    st.markdown("# Raw Predictions Log")
    st.markdown("<p style='color:#6b7280;margin-top:-12px;font-size:1rem'>Full dataset with scores, flags, and filtering</p>", unsafe_allow_html=True)
    st.divider()

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filter_opt = st.radio("Show:", ["All", "Bots only", "Humans only"], horizontal=True)
    with col_f2:
        search_score = st.slider("Min score", 0.0, 1.0, 0.0, 0.01)

    display_df = preds.copy()
    display_df["victor_flag"] = (display_df["ensemble_score"] > threshold).astype(int)

    if filter_opt == "Bots only":
        display_df = display_df[display_df["victor_flag"] == 1]
    elif filter_opt == "Humans only":
        display_df = display_df[display_df["victor_flag"] == 0]

    display_df = display_df[display_df["ensemble_score"] >= search_score]

    cols_to_show = [c for c in [*FEATURE_COLS, "iso_score", "xgb_score", "ensemble_score", "victor_flag"] if c in display_df.columns]
    display_df = display_df[cols_to_show].sort_values("ensemble_score", ascending=False).reset_index(drop=True)

    for col in ["iso_score", "xgb_score", "ensemble_score"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(3)

    def style_row(row):
        status = "<span class='badge-bot'>BOT</span>" if row.get("victor_flag", 0) == 1 else "<span class='badge-human'>HUMAN</span>"
        return status

    display_df["status"] = display_df.apply(style_row, axis=1)
    display_df = display_df.drop(columns=["victor_flag"], errors="ignore")

    html_table = display_df.to_html(index=False, escape=False)
    st.markdown(f"<div class='victor-table-wrap'>{html_table}</div>", unsafe_allow_html=True)
    st.caption(f"Showing {len(display_df):,} of {len(preds):,} total requests  •  threshold = {threshold}")