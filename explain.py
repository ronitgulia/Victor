import shap
import joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

os.makedirs("data/shap", exist_ok=True)

model = joblib.load("models/xgboost_model.pkl")
df    = pd.read_csv("data/features.csv")

FEATURE_COLS = [
    "ua_is_suspicious",
    "has_referer",
    "has_accept_lang",
    "hit_secret_page",
    "ua_length",
    "time_gap_seconds",
    "unique_pages_visited",
    "total_requests_from_ip"
]

X = df[FEATURE_COLS]

print("Computing SHAP values (this takes a few seconds)...")
explainer   = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

print("Done.")

print("Saving global feature importance plot...")

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X, show=False)
plt.title("Victor — Feature Importance (SHAP)")
plt.tight_layout()
plt.savefig("data/shap/global_summary.png", dpi=150, bbox_inches="tight")
plt.close()

print("  Saved -> data/shap/global_summary.png")

print("Saving bar chart version...")

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X, plot_type="bar", show=False)
plt.title("Victor — Average Feature Impact")
plt.tight_layout()
plt.savefig("data/shap/feature_bar.png", dpi=150, bbox_inches="tight")
plt.close()

print("  Saved -> data/shap/feature_bar.png")

shap_df = pd.DataFrame(shap_values, columns=[f"shap_{c}" for c in FEATURE_COLS])
shap_df.to_csv("data/shap/shap_values.csv", index=False)

print("  Saved -> data/shap/shap_values.csv")
print("\nSHAP explainability complete.")