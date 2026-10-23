"""
Clinical Disease Predictor Module for Patient Tracker.
Provides multi-model AI inference, top-3 differential diagnosis ranking,
and SHAP / feature contribution explainability.

Includes safety guards so the web application never crashes if a model artifact
is temporarily missing, providing friendly fallbacks and clear logging.

Disclaimer: AI assistance only, not a medical diagnosis.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import joblib

from app.ai.symptom_analyzer import format_symptom_display_name
from app.ai.disease_info import get_disease_description, get_recommended_specialization

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, 'model')

MODEL_PATH = os.path.join(MODEL_DIR, 'disease_model.joblib')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.joblib')
VOCAB_PATH = os.path.join(MODEL_DIR, 'symptom_vocab.json')

DISCLAIMER_TEXT = "AI assistance only, not a medical diagnosis"

# -------------------------------------------------------------------------
# SAFE ARTIFACT LOADING
# -------------------------------------------------------------------------
_model = None
_label_encoder = None
_vocab = None
_shap_explainer = None


def load_artifacts():
    """Safely loads model, label encoder, and vocabulary with graceful error recovery."""
    global _model, _label_encoder, _vocab
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(LABEL_ENCODER_PATH) and os.path.exists(VOCAB_PATH):
            _model = joblib.load(MODEL_PATH)
            _label_encoder = joblib.load(LABEL_ENCODER_PATH)
            with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
                _vocab = json.load(f)
            logger.info("Successfully loaded disease prediction model artifacts.")
        else:
            logger.warning("One or more disease prediction model artifacts are missing in %s", MODEL_DIR)
    except Exception as e:
        logger.error("Error loading disease prediction artifacts: %s", str(e), exc_info=True)
        _model, _label_encoder, _vocab = None, None, None


# Attempt artifact load on module import
load_artifacts()


class PredictionResult(tuple):
    """
    Subclasses tuple (primary_disease, primary_confidence) for 100% backward compatibility
    with legacy unpacking:
        predicted_disease, confidence = predict_disease(symptoms)

    While also delivering full Feature 1 multi-prediction and explainability data:
        result.top_predictions  -> List of Top-3 predictions with probabilities and specs
        result.explainability   -> List of patient's contributing symptoms with relative weights
        result.disclaimer       -> "AI assistance only, not a medical diagnosis"
        result.primary_disease  -> Name of top disease
        result.confidence       -> Confidence percentage of top disease
    """
    def __new__(cls, primary_disease, confidence, top_predictions=None, explainability=None, disclaimer=DISCLAIMER_TEXT):
        return super().__new__(cls, (primary_disease, confidence))

    def __init__(self, primary_disease, confidence, top_predictions=None, explainability=None, disclaimer=DISCLAIMER_TEXT):
        self.primary_disease = primary_disease
        self.confidence = confidence
        self.top_predictions = top_predictions or []
        self.explainability = explainability or []
        self.disclaimer = disclaimer


def _calculate_explainability(model, feature_vector_df, active_symptoms, top_class_idx, vocab):
    """
    Computes explainability scores showing which of the patient's active symptoms
    contributed most to predicting the primary disease class.
    Uses SHAP LinearExplainer with fallback to model log-odds coefficients.
    """
    contributions = []
    if not active_symptoms:
        return contributions

    # 1. Attempt SHAP explanation
    shap_calculated = False
    try:
        import shap
        # Baseline zero vector representing asymptomatic state
        zero_background = pd.DataFrame(np.zeros((1, len(vocab))), columns=vocab)
        explainer = shap.LinearExplainer(model, zero_background)
        shap_vals = explainer(feature_vector_df)

        for sym in active_symptoms:
            if sym in vocab:
                col_idx = vocab.index(sym)
                # Value for top predicted class
                val = float(shap_vals.values[0, col_idx, top_class_idx])
                contributions.append({
                    'code': sym,
                    'name': format_symptom_display_name(sym),
                    'raw_score': max(0.0, val)
                })
        shap_calculated = True
    except Exception as e:
        logger.warning("SHAP calculation skipped or failed (%s); falling back to model coefficients.", str(e))

    # 2. Fallback: Log-odds coefficients from LogisticRegression
    if not shap_calculated or all(c['raw_score'] == 0.0 for c in contributions):
        contributions = []
        try:
            if hasattr(model, 'coef_'):
                class_coefs = model.coef_[top_class_idx]
                for sym in active_symptoms:
                    if sym in vocab:
                        col_idx = vocab.index(sym)
                        weight = float(class_coefs[col_idx])
                        contributions.append({
                            'code': sym,
                            'name': format_symptom_display_name(sym),
                            'raw_score': max(0.001, weight)
                        })
            elif hasattr(model, 'feature_importances_'):
                for sym in active_symptoms:
                    if sym in vocab:
                        col_idx = vocab.index(sym)
                        weight = float(model.feature_importances_[col_idx])
                        contributions.append({
                            'code': sym,
                            'name': format_symptom_display_name(sym),
                            'raw_score': max(0.001, weight)
                        })
        except Exception as e:
            logger.warning("Coefficient explanation fallback failed: %s", str(e))

    # If still empty or all zeros, assign equal baseline weights
    if not contributions:
        for sym in active_symptoms:
            contributions.append({
                'code': sym,
                'name': format_symptom_display_name(sym),
                'raw_score': 1.0
            })

    total_score = sum(c['raw_score'] for c in contributions)
    if total_score <= 0.0:
        total_score = len(contributions)
        for c in contributions:
            c['raw_score'] = 1.0

    # Calculate percentage contributions and assign impact badges
    for c in contributions:
        pct = round((c['raw_score'] / total_score) * 100, 1)
        c['percentage'] = pct
        if pct >= 35.0:
            c['impact'] = 'Key Driver'
            c['impact_badge'] = 'danger'
        elif pct >= 20.0:
            c['impact'] = 'Strong Sign'
            c['impact_badge'] = 'primary'
        else:
            c['impact'] = 'Supporting'
            c['impact_badge'] = 'secondary'

    # Sort descending by contribution percentage
    contributions.sort(key=lambda x: x['percentage'], reverse=True)
    return contributions


def predict_disease(symptoms_list, return_top_3=False):
    """
    Takes a list of symptoms (e.g. ['fever', 'headache', 'body pain'] or ['high_fever', 'headache'])
    and returns a PredictionResult with Top-3 predictions and SHAP explainability.

    Maintains 100% backward compatibility:
    - Primary prediction stays at index 0 for (predicted_disease, confidence) unpacking.
    - If model artifact is missing, returns safe fallback and does not crash.
    """
    global _model, _label_encoder, _vocab
    if _model is None or _label_encoder is None or _vocab is None:
        load_artifacts()

    # Safety check: if model artifacts are unavailable
    if _model is None or _label_encoder is None or _vocab is None:
        logger.warning("Disease prediction attempted but model artifacts are not loaded.")
        empty_res = PredictionResult(
            None,
            0.0,
            top_predictions=[],
            explainability=[],
            disclaimer=DISCLAIMER_TEXT
        )
        return empty_res.top_predictions if return_top_3 else empty_res

    if not symptoms_list:
        empty_res = PredictionResult(
            None,
            0.0,
            top_predictions=[],
            explainability=[],
            disclaimer=DISCLAIMER_TEXT
        )
        return empty_res.top_predictions if return_top_3 else empty_res

    # Build 132-dimension binary feature vector matching training columns
    feature_vector = np.zeros((1, len(_vocab)), dtype=int)
    active_symptoms = []

    for item in symptoms_list:
        clean_code = str(item).strip().lower().replace(' ', '_')
        # Check direct code or underscored version
        if clean_code in _vocab:
            idx = _vocab.index(clean_code)
            feature_vector[0, idx] = 1
            active_symptoms.append(clean_code)
        elif str(item).strip() in _vocab:
            idx = _vocab.index(str(item).strip())
            feature_vector[0, idx] = 1
            active_symptoms.append(str(item).strip())

    feature_df = pd.DataFrame(feature_vector, columns=_vocab)

    # In case no recognized symptom matched vocabulary
    if not active_symptoms:
        empty_res = PredictionResult(
            None,
            0.0,
            top_predictions=[],
            explainability=[],
            disclaimer=DISCLAIMER_TEXT
        )
        return empty_res.top_predictions if return_top_3 else empty_res

    try:
        # Predict class probabilities across all 41 diseases
        probabilities = _model.predict_proba(feature_df)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_classes = _label_encoder.inverse_transform(top_indices)
        top_probs = probabilities[top_indices]

        top_predictions = []
        for rank, (disease_name, prob) in enumerate(zip(top_classes, top_probs), start=1):
            disease_str = str(disease_name).strip()
            conf_pct = round(float(prob) * 100, 2)
            spec = get_recommended_specialization(disease_str)
            desc = get_disease_description(disease_str)

            top_predictions.append({
                'rank': rank,
                'disease': disease_str,
                'probability': round(float(prob), 4),
                'confidence': conf_pct,
                'specialization': spec,
                'description': desc
            })

        primary_disease = top_predictions[0]['disease']
        primary_confidence = top_predictions[0]['confidence']

        # Explainability for top class
        top_class_idx = int(top_indices[0])
        explainability = _calculate_explainability(_model, feature_df, active_symptoms, top_class_idx, _vocab)

        result = PredictionResult(
            primary_disease,
            primary_confidence,
            top_predictions=top_predictions,
            explainability=explainability,
            disclaimer=DISCLAIMER_TEXT
        )

        if return_top_3:
            return top_predictions
        return result

    except Exception as e:
        logger.error("Error during disease prediction inference: %s", str(e), exc_info=True)
        return PredictionResult(
            None,
            0.0,
            top_predictions=[],
            explainability=[],
            disclaimer=DISCLAIMER_TEXT
        )