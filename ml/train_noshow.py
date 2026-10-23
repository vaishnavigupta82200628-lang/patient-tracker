"""
No-Show Prediction training script.
Run from the project root:  python ml/train_noshow.py            (full data)
                            python ml/train_noshow.py --sample   (50,000 rows, quick test)
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix, roc_curve)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "ml", "data", "noshow", "KaggleV2-May-2016.csv")
MODEL_DIR = os.path.join(ROOT, "app", "ai", "model")
PLOT_DIR = os.path.join(ROOT, "app", "static", "ml_reports")
REPORT = os.path.join(ROOT, "ml", "reports", "noshow_metrics.json")
for d in (MODEL_DIR, PLOT_DIR, os.path.dirname(REPORT)):
    os.makedirs(d, exist_ok=True)

FEATURES = ["age", "gender_male", "lead_days", "dow", "prev_appts", "prev_noshows"]

# ---------- 1. Load and clean ----------
df = pd.read_csv(DATA)
df = df.rename(columns={"No-show": "no_show", "Hipertension": "hypertension", "Handcap": "handicap"})
df["scheduled"] = pd.to_datetime(df["ScheduledDay"], utc=True).dt.tz_localize(None)
df["appt_date"] = pd.to_datetime(df["AppointmentDay"], utc=True).dt.tz_localize(None).dt.normalize()
df["target"] = (df["no_show"] == "Yes").astype(int)
df = df[(df["Age"] >= 0) & (df["Age"] <= 100)]

# lead time in days (appointment date minus the day it was booked)
df["lead_days"] = (df["appt_date"] - df["scheduled"].dt.normalize()).dt.days
df = df[df["lead_days"] >= 0]          # remove impossible negative lead times

df["age"] = df["Age"]
df["gender_male"] = (df["Gender"] == "M").astype(int)
df["dow"] = df["appt_date"].dt.dayofweek

# ---------- 2. History features (only EARLIER appointments -> no leakage) ----------
df = df.sort_values(["PatientId", "appt_date", "scheduled"]).reset_index(drop=True)
grp = df.groupby("PatientId")
df["prev_appts"] = grp.cumcount()
df["prev_noshows"] = grp["target"].cumsum() - df["target"]

if "--sample" in sys.argv:
    df = df.sample(50000, random_state=42)
    print("QUICK MODE: using a 50,000 row sample")

X, y = df[FEATURES], df["target"]
print(f"Rows: {len(df)}   No-show rate: {y.mean():.3f}")

# Split by time-agnostic stratified random split (simple, reproducible)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# ---------- 3. Models ----------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, min_samples_leaf=20,
                                            class_weight="balanced", n_jobs=-1, random_state=42),
    "Gradient Boosting": HistGradientBoostingClassifier(max_depth=6, learning_rate=0.08,
                                                        class_weight="balanced", random_state=42),
}

results, probs = {}, {}
for name, m in models.items():
    print("Training", name, "...")
    m.fit(X_tr, y_tr)
    p = m.predict_proba(X_te)[:, 1]
    pred = (p >= 0.5).astype(int)
    probs[name] = p
    results[name] = {
        "accuracy": round(accuracy_score(y_te, pred), 4),
        "precision": round(precision_score(y_te, pred, zero_division=0), 4),
        "recall": round(recall_score(y_te, pred), 4),
        "f1": round(f1_score(y_te, pred), 4),
        "roc_auc": round(roc_auc_score(y_te, p), 4),
        "pr_auc": round(average_precision_score(y_te, p), 4),
        "confusion_matrix": confusion_matrix(y_te, pred).tolist(),
    }
    print("  ", {k: v for k, v in results[name].items() if k != "confusion_matrix"})

# ---------- 4. Pick best by ROC-AUC ----------
best = max(results, key=lambda k: results[k]["roc_auc"])
print("\nBest model:", best)

# ---------- 5. Plots ----------
plt.figure(figsize=(6, 5))
for name, p in probs.items():
    fpr, tpr, _ = roc_curve(y_te, p)
    plt.plot(fpr, tpr, label=f"{name} (AUC={results[name]['roc_auc']})")
plt.plot([0, 1], [0, 1], "k--", label="Random guess")
plt.xlabel("False positive rate"); plt.ylabel("True positive rate")
plt.title("No-show prediction: ROC curves"); plt.legend(); plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "noshow_roc.png"), dpi=120); plt.close()

names = list(results)
x = np.arange(len(names)); w = 0.2
plt.figure(figsize=(8, 5))
for i, metric in enumerate(["accuracy", "recall", "f1", "roc_auc"]):
    plt.bar(x + i * w, [results[n][metric] for n in names], w, label=metric)
plt.xticks(x + 1.5 * w, names); plt.ylim(0, 1); plt.legend()
plt.title("No-show prediction: model comparison"); plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "noshow_comparison.png"), dpi=120); plt.close()

# ---------- 6. Save ----------
joblib.dump({"model": models[best], "features": FEATURES, "name": best},
            os.path.join(MODEL_DIR, "noshow_model.joblib"))
with open(REPORT, "w") as f:
    json.dump({"dataset": "Kaggle Medical Appointment No Shows (Brazil, 2016)",
               "rows_used": int(len(df)), "no_show_rate": round(float(y.mean()), 4),
               "features": FEATURES, "best_model": best, "models": results,
               "note": "Accuracy alone is misleading: ~80% of patients show up, so a model that always "
                       "predicts 'will attend' gets ~80% accuracy but catches zero no-shows. "
                       "Recall, ROC-AUC and PR-AUC are the meaningful metrics here."}, f, indent=2)
print("Saved model, plots and metrics.")