"""
Offline Training Script for Disease Prediction Models.
Compares 7 algorithms with 5-fold Stratified Cross-Validation, evaluates robustness
under noisy test conditions, exports metrics, saves visualization plots,
and serializes the best performing model with symptom vocabulary and label encoder.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# Algorithms
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------
# PATH CONFIGURATION
# -------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'ml', 'data', 'disease')
REPORTS_DIR = os.path.join(BASE_DIR, 'ml', 'reports')
STATIC_REPORTS_DIR = os.path.join(BASE_DIR, 'app', 'static', 'ml_reports')
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'ai', 'model')

TRAIN_PATH = os.path.join(DATA_DIR, 'Training.csv')
TEST_PATH = os.path.join(DATA_DIR, 'Testing.csv')


def load_and_clean_data(train_csv_path, test_csv_path):
    """
    Loads Training.csv and Testing.csv, cleans whitespace, drops stray columns,
    and deduplicates data to prevent data leakage across validation folds.
    """
    if not os.path.exists(train_csv_path) or not os.path.exists(test_csv_path):
        raise FileNotFoundError(f"Dataset files not found in {DATA_DIR}")

    df_train = pd.read_csv(train_csv_path)
    df_test = pd.read_csv(test_csv_path)

    # 1. Clean column headers (strip whitespace, remove unnamed stray columns)
    for df in [df_train, df_test]:
        unnamed_cols = [c for c in df.columns if 'Unnamed' in c]
        if unnamed_cols:
            df.drop(columns=unnamed_cols, inplace=True, errors='ignore')
        df.columns = [c.strip() for c in df.columns]

    # 2. Clean disease label whitespace (e.g. 'Diabetes ', 'Hypertension ')
    df_train['prognosis'] = df_train['prognosis'].astype(str).str.strip()
    df_test['prognosis'] = df_test['prognosis'].astype(str).str.strip()

    # 3. Combine both official splits for unified deduplicated training pool
    df_combined = pd.concat([df_train, df_test], ignore_index=True)

    # Remove exact duplicate records
    raw_count = len(df_combined)
    df_clean = df_combined.drop_duplicates().reset_index(drop=True)
    dedup_count = len(df_clean)

    symptom_cols = [c for c in df_clean.columns if c != 'prognosis']
    diseases = sorted(df_clean['prognosis'].unique())

    print(f"[*] Raw samples: {raw_count} | Clean unique profiles: {dedup_count}")
    print(f"[*] Verified {len(symptom_cols)} symptoms across {len(diseases)} diseases.")

    return df_clean, symptom_cols, diseases


def create_noisy_test_set(X_test, random_state=42):
    """
    Robustness evaluation helper:
    Randomly drops 20% to 40% of active symptoms and adds 1 to 2 random false symptoms
    to simulate realistic, imperfect patient reporting.
    """
    np.random.seed(random_state)
    X_noisy = np.array(X_test, copy=True)

    for i in range(len(X_noisy)):
        ones_idx = np.where(X_noisy[i] == 1)[0]
        zeros_idx = np.where(X_noisy[i] == 0)[0]

        # Drop 20-40% of patient's true symptoms
        if len(ones_idx) > 1:
            drop_fraction = np.random.uniform(0.20, 0.40)
            n_drop = max(1, int(round(len(ones_idx) * drop_fraction)))
            drop_indices = np.random.choice(ones_idx, size=min(n_drop, len(ones_idx) - 1), replace=False)
            X_noisy[i, drop_indices] = 0

        # Inject 1-2 random irrelevant/wrong symptoms
        if len(zeros_idx) > 2:
            n_add = np.random.choice([1, 2])
            add_indices = np.random.choice(zeros_idx, size=n_add, replace=False)
            X_noisy[i, add_indices] = 1

    return X_noisy


def train_and_evaluate_all():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(STATIC_REPORTS_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

    df_clean, symptom_cols, diseases = load_and_clean_data(TRAIN_PATH, TEST_PATH)

    X = df_clean[symptom_cols]
    y_raw = df_clean['prognosis']

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    # Stratified 80/20 train-test split for held-out evaluation & robustness testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    X_test_noisy = create_noisy_test_set(X_test, random_state=42)

    # 7 Candidate Classifiers
    candidate_models = {
        'Naive Bayes': MultinomialNB(),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='linear', probability=True, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=3),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss')
    }

    # 5-fold Stratified Cross-Validation on the full cleaned dataset
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring_metrics = {
        'accuracy': 'accuracy',
        'precision_macro': 'precision_macro',
        'recall_macro': 'recall_macro',
        'f1_macro': 'f1_macro'
    }

    results = {}
    fitted_models = {}

    print("\n" + "=" * 95)
    print(f"{'Model':<22} | {'CV Accuracy':<16} | {'Test Acc':<9} | {'Macro F1':<9} | {'Noisy Acc':<9} | {'Status'}")
    print("=" * 95)

    for name, model in candidate_models.items():
        # Cross validation scores across 5 stratified folds
        cv_res = cross_validate(model, X, y, cv=cv_strategy, scoring=scoring_metrics)
        cv_acc_mean = float(np.mean(cv_res['test_accuracy']))
        cv_acc_std = float(np.std(cv_res['test_accuracy']))
        cv_f1_mean = float(np.mean(cv_res['test_f1_macro']))
        cv_prec_mean = float(np.mean(cv_res['test_precision_macro']))
        cv_recall_mean = float(np.mean(cv_res['test_recall_macro']))

        # Fit on train split for held-out clean and noisy test evaluation
        model.fit(X_train, y_train)
        fitted_models[name] = model

        y_pred = model.predict(X_test)
        test_acc = float(accuracy_score(y_test, y_pred))
        test_prec = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
        test_recall = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
        test_f1 = float(f1_score(y_test, y_pred, average='macro', zero_division=0))

        # Noisy robustness evaluation
        y_pred_noisy = model.predict(X_test_noisy)
        noisy_acc = float(accuracy_score(y_test, y_pred_noisy))

        results[name] = {
            'cv_accuracy_mean': round(cv_acc_mean, 4),
            'cv_accuracy_std': round(cv_acc_std, 4),
            'cv_f1_macro_mean': round(cv_f1_mean, 4),
            'cv_precision_macro_mean': round(cv_prec_mean, 4),
            'cv_recall_macro_mean': round(cv_recall_mean, 4),
            'test_accuracy': round(test_acc, 4),
            'test_precision_macro': round(test_prec, 4),
            'test_recall_macro': round(test_recall, 4),
            'test_f1_macro': round(test_f1, 4),
            'noisy_test_accuracy': round(noisy_acc, 4)
        }

        cv_str = f"{cv_acc_mean*100:.2f}% +/- {cv_acc_std*100:.2f}%"
        print(f"{name:<22} | {cv_str:<16} | {test_acc*100:>7.2f}% | {test_f1*100:>7.2f}% | {noisy_acc*100:>7.2f}% | Evaluated")

    print("=" * 95)

    # Select best model:
    # Primary sort: cv_accuracy_mean (highest)
    # Secondary sort: noisy_test_accuracy (highest robustness)
    # Tertiary sort: cv_accuracy_std (lowest variance)
    best_model_name = max(
        results.keys(),
        key=lambda m: (
            results[m]['cv_accuracy_mean'],
            results[m]['noisy_test_accuracy'],
            -results[m]['cv_accuracy_std']
        )
    )
    best_model = fitted_models[best_model_name]
    print(f"\n[BEST] Best Selected Model: {best_model_name}")
    print(f"       CV Mean Accuracy : {results[best_model_name]['cv_accuracy_mean']*100:.2f}%")
    print(f"       Noisy Robustness : {results[best_model_name]['noisy_test_accuracy']*100:.2f}%")

    # Fit best model on the full cleaned dataset for production deployment
    final_production_model = candidate_models[best_model_name]
    final_production_model.fit(X, y)

    # -------------------------------------------------------------------------
    # GENERATE AND SAVE PLOTS
    # -------------------------------------------------------------------------
    # Plot 1: Model Comparison Bar Chart
    plt.figure(figsize=(12, 6), dpi=300)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    model_names = list(results.keys())
    cv_means = [results[m]['cv_accuracy_mean'] * 100 for m in model_names]
    test_accs = [results[m]['test_accuracy'] * 100 for m in model_names]
    noisy_accs = [results[m]['noisy_test_accuracy'] * 100 for m in model_names]

    x_indices = np.arange(len(model_names))
    bar_width = 0.25

    plt.bar(x_indices - bar_width, cv_means, width=bar_width, label='5-Fold CV Accuracy (%)', color='#0B5ED7', alpha=0.9)
    plt.bar(x_indices, test_accs, width=bar_width, label='Held-Out Test Accuracy (%)', color='#0284C7', alpha=0.9)
    plt.bar(x_indices + bar_width, noisy_accs, width=bar_width, label='Robustness (Noisy Test) (%)', color='#D97706', alpha=0.9)

    plt.ylabel('Score (%)', fontsize=12, fontweight='bold')
    plt.title('Disease Prediction Models: Performance & Robustness Comparison', fontsize=14, fontweight='bold', pad=15)
    plt.xticks(x_indices, model_names, rotation=20, ha='right', fontsize=11)
    plt.ylim(0, 115)
    plt.legend(frameon=True, loc='upper left', fontsize=10)
    plt.tight_layout()

    comparison_plot_path = os.path.join(STATIC_REPORTS_DIR, 'model_comparison.png')
    plt.savefig(comparison_plot_path)
    plt.close()
    print(f"[*] Comparison chart saved to: {comparison_plot_path}")

    # Plot 2: Confusion Matrix of Best Model on Held-out test set
    y_best_pred = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_best_pred)

    plt.figure(figsize=(14, 12), dpi=300)
    sns.heatmap(cm, annot=False, cmap='Blues', cbar=True, square=True)
    plt.title(f'Confusion Matrix — Best Model ({best_model_name}) on Held-Out Test Data', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Predicted Disease Class', fontsize=12)
    plt.ylabel('True Disease Class', fontsize=12)
    plt.tight_layout()

    cm_plot_path = os.path.join(STATIC_REPORTS_DIR, 'best_model_confusion_matrix.png')
    plt.savefig(cm_plot_path)
    plt.close()
    print(f"[*] Confusion matrix saved to: {cm_plot_path}")

    # -------------------------------------------------------------------------
    # SAVE METRICS & ARTIFACTS
    # -------------------------------------------------------------------------
    metrics_export = {
        'best_model': best_model_name,
        'symptoms_count': len(symptom_cols),
        'diseases_count': len(diseases),
        'clean_samples_count': len(df_clean),
        'robustness_drop_rate': '20% to 40% active symptoms dropped, 1-2 random symptoms added',
        'limitation_statement': (
            'The disease dataset is synthetic and demonstrates high baseline accuracy (~100%) on clean data. '
            'However, real clinical patient presentations feature missing symptoms, subjective reporting, and comorbidity. '
            f'Under simulated noisy conditions, model accuracy adjusts (best: {results[best_model_name]["noisy_test_accuracy"]*100:.1f}%), '
            'confirming that predictions are decision-support estimates rather than definitive medical diagnoses.'
        ),
        'models': results
    }

    metrics_json_path = os.path.join(REPORTS_DIR, 'disease_metrics.json')
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_export, f, indent=4)
    print(f"[*] Metrics JSON saved to: {metrics_json_path}")

    # Save model artifacts for production
    model_save_path = os.path.join(MODEL_DIR, 'disease_model.joblib')
    joblib.dump(final_production_model, model_save_path)

    # Also save label encoder and symptom vocabulary list
    le_save_path = os.path.join(MODEL_DIR, 'label_encoder.joblib')
    joblib.dump(label_encoder, le_save_path)

    vocab_save_path = os.path.join(MODEL_DIR, 'symptom_vocab.json')
    with open(vocab_save_path, 'w', encoding='utf-8') as f:
        json.dump(symptom_cols, f, indent=2)

    meta_save_path = os.path.join(MODEL_DIR, 'metadata.json')
    with open(meta_save_path, 'w', encoding='utf-8') as f:
        json.dump({
            'best_model': best_model_name,
            'symptom_count': len(symptom_cols),
            'disease_count': len(diseases),
            'cv_mean': results[best_model_name]['cv_accuracy_mean'],
            'noisy_accuracy': results[best_model_name]['noisy_test_accuracy']
        }, f, indent=2)

    print(f"[*] Model artifacts successfully saved to {MODEL_DIR}")
    return metrics_export


if __name__ == '__main__':
    train_and_evaluate_all()
