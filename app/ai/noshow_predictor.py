"""
No-Show Predictor Module for Patient Tracker.
Predicts the likelihood of a patient missing a scheduled appointment
using the pre-trained Gradient Boosting model artifact.

Returns (probability 0-1, risk_level) with risk_level in ("Low", "Medium", "High"),
or None if the model is unavailable.
"""

import os
import logging
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'model', 'noshow_model.joblib')

_model_bundle = None
_load_attempted = False


def load_noshow_model():
    """Safely loads the no-show model artifact from disk."""
    global _model_bundle, _load_attempted
    _load_attempted = True
    try:
        if os.path.exists(MODEL_PATH):
            _model_bundle = joblib.load(MODEL_PATH)
            logger.info("Successfully loaded no-show prediction model from %s", MODEL_PATH)
        else:
            logger.warning("No-show model artifact not found at %s", MODEL_PATH)
            _model_bundle = None
    except Exception as e:
        logger.error("Error loading no-show model: %s", str(e), exc_info=True)
        _model_bundle = None
    return _model_bundle


def get_model_bundle():
    global _model_bundle, _load_attempted
    if not _load_attempted:
        load_noshow_model()
    return _model_bundle


def predict_no_show(appointment):
    """
    Predicts appointment no-show probability and risk category.

    Args:
        appointment: An Appointment SQLAlchemy model instance.

    Returns:
        tuple (probability, risk_level) where:
            probability is a float between 0.0 and 1.0,
            risk_level is one of "Low", "Medium", "High".
        Returns None if model is unavailable or prediction cannot be made.
    """
    bundle = get_model_bundle()
    if not bundle:
        return None

    try:
        model = bundle.get('model')
        features = bundle.get('features', ["age", "gender_male", "lead_days", "dow", "prev_appts", "prev_noshows"])
        if model is None:
            return None

        # 1. Patient demographic features
        patient = getattr(appointment, 'patient', None)
        age = 37.0  # default population average
        gender_male = 0

        if patient:
            if getattr(patient, 'age', None) is not None:
                try:
                    age = float(patient.age)
                except (ValueError, TypeError):
                    age = 37.0
            if getattr(patient, 'gender', None):
                gender_str = str(patient.gender).strip().lower()
                gender_male = 1 if gender_str in ['m', 'male'] else 0

        # 2. Appointment timing & lead time
        appt_dt = getattr(appointment, 'date_time', None)
        created_dt = getattr(appointment, 'created_at', None) or appt_dt

        lead_days = 0
        dow = 0
        if appt_dt:
            dow = appt_dt.weekday()
            if created_dt:
                try:
                    delta = (appt_dt.date() - created_dt.date()).days
                    lead_days = max(0, delta)
                except Exception:
                    lead_days = 0

        # 3. Patient historical attendance features
        prev_appts = 0
        prev_noshows = 0
        patient_id = getattr(appointment, 'patient_id', None)

        if patient_id:
            try:
                from app.models import Appointment
                query = Appointment.query.filter(Appointment.patient_id == patient_id)
                if getattr(appointment, 'id', None):
                    query = query.filter(Appointment.id != appointment.id)
                if appt_dt:
                    query = query.filter(Appointment.date_time < appt_dt)

                prev_appts = query.count()
                prev_noshows = query.filter(Appointment.status == 'no_show').count()
            except Exception as hist_err:
                logger.debug("Could not compute historical attendance: %s", hist_err)
                prev_appts = 0
                prev_noshows = 0

        row = {
            'age': age,
            'gender_male': gender_male,
            'lead_days': lead_days,
            'dow': dow,
            'prev_appts': prev_appts,
            'prev_noshows': prev_noshows
        }
        df_input = pd.DataFrame([row])[features]

        # 4. Predict probability
        probs = model.predict_proba(df_input)
        # Class 1 is 'no_show'
        prob = float(probs[0, 1])
        prob = max(0.0, min(1.0, prob))

        # 5. Risk classification
        if prob >= 0.50:
            risk_level = "High"
        elif prob >= 0.30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return (round(prob, 4), risk_level)

    except Exception as e:
        logger.warning("Error running no-show prediction for appointment %s: %s",
                       getattr(appointment, 'id', 'unknown'), str(e))
        return None
