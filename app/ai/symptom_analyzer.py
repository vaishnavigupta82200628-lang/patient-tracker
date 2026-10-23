"""
Natural Language Symptom Extractor for Patient Tracker.
Extracts clinical symptoms from conversational patient descriptions using NLTK
(tokenization, stopword filtering) and maps colloquial expressions / synonyms
to the exact 132 symptom feature names in our ML training vocabulary.
"""

import os
import json
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Ensure necessary NLTK data packages are available
for pkg in ['punkt', 'punkt_tab', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{pkg}' if 'punkt' in pkg else f'corpora/{pkg}')
    except LookupError:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

# Load master 132-symptom vocabulary from trained model artifacts
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_PATH = os.path.join(CURRENT_DIR, 'model', 'symptom_vocab.json')

if os.path.exists(VOCAB_PATH):
    with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
        DATASET_SYMPTOMS = json.load(f)
else:
    DATASET_SYMPTOMS = []

# Comprehensive synonym dictionary mapping colloquial phrases to exact dataset features
SYNONYM_MAP = {
    # Fevers
    'fever': 'high_fever',
    'high fever': 'high_fever',
    'feverish': 'high_fever',
    'high temperature': 'high_fever',
    'mild fever': 'mild_fever',
    'low fever': 'mild_fever',
    'slight fever': 'mild_fever',

    # Pains & Aches
    'headache': 'headache',
    'head ache': 'headache',
    'severe headache': 'headache',
    'throbbing headache': 'headache',
    'migraine': 'headache',
    'body pain': 'muscle_pain',
    'body ache': 'muscle_pain',
    'body aches': 'muscle_pain',
    'aching body': 'muscle_pain',
    'muscle pain': 'muscle_pain',
    'muscle ache': 'muscle_pain',
    'muscle aches': 'muscle_pain',
    'joint pain': 'joint_pain',
    'joints pain': 'joint_pain',
    'joint ache': 'joint_pain',
    'knee pain': 'knee_pain',
    'hip pain': 'hip_joint_pain',
    'hip joint pain': 'hip_joint_pain',
    'back pain': 'back_pain',
    'backache': 'back_pain',
    'lower back pain': 'back_pain',
    'neck pain': 'neck_pain',
    'stiff neck': 'stiff_neck',
    'chest pain': 'chest_pain',
    'chest tightness': 'chest_pain',
    'chest pressure': 'chest_pain',
    'eye pain': 'pain_behind_the_eyes',
    'pain behind the eyes': 'pain_behind_the_eyes',
    'pain behind eyes': 'pain_behind_the_eyes',
    'pain in anal region': 'pain_in_anal_region',
    'pain during bowel movements': 'pain_during_bowel_movements',

    # Digestive & Abdominal
    'stomach pain': 'stomach_pain',
    'stomach ache': 'stomach_pain',
    'tummy ache': 'stomach_pain',
    'belly pain': 'belly_pain',
    'abdominal pain': 'abdominal_pain',
    'stomach cramps': 'stomach_pain',
    'acidity': 'acidity',
    'heartburn': 'acidity',
    'acid reflux': 'acidity',
    'indigestion': 'indigestion',
    'upset stomach': 'indigestion',
    'vomiting': 'vomiting',
    'throwing up': 'vomiting',
    'puking': 'vomiting',
    'nausea': 'nausea',
    'feeling sick': 'nausea',
    'queasy': 'nausea',
    'diarrhea': 'diarrhoea',
    'diarrhoea': 'diarrhoea',
    'loose motions': 'diarrhoea',
    'loose motion': 'diarrhoea',
    'watery stool': 'diarrhoea',
    'constipation': 'constipation',
    'passage of gases': 'passage_of_gases',
    'gas': 'passage_of_gases',
    'flatulence': 'passage_of_gases',
    'stomach bleeding': 'stomach_bleeding',
    'distention of abdomen': 'distention_of_abdomen',
    'bloating': 'distention_of_abdomen',
    'swelling of stomach': 'swelling_of_stomach',

    # Respiratory & Cold
    'cough': 'cough',
    'coughing': 'cough',
    'dry cough': 'cough',
    'wet cough': 'cough',
    'runny nose': 'runny_nose',
    'running nose': 'runny_nose',
    'blocked nose': 'congestion',
    'congestion': 'congestion',
    'nasal congestion': 'congestion',
    'cold': 'continuous_sneezing',
    'sneezing': 'continuous_sneezing',
    'continuous sneezing': 'continuous_sneezing',
    'shortness of breath': 'breathlessness',
    'breathlessness': 'breathlessness',
    'difficulty breathing': 'breathlessness',
    'hard to breathe': 'breathlessness',
    'phlegm': 'phlegm',
    'mucus': 'phlegm',
    'throat irritation': 'throat_irritation',
    'sore throat': 'throat_irritation',
    'itchy throat': 'throat_irritation',
    'sinus pressure': 'sinus_pressure',
    'sinus pain': 'sinus_pressure',
    'blood in sputum': 'blood_in_sputum',
    'rusty sputum': 'rusty_sputum',
    'mucoid sputum': 'mucoid_sputum',

    # Systemic & General
    'fatigue': 'fatigue',
    'tiredness': 'fatigue',
    'exhaustion': 'fatigue',
    'lethargy': 'lethargy',
    'weakness': 'fatigue',
    'weakness in limbs': 'weakness_in_limbs',
    'muscle weakness': 'muscle_weakness',
    'chills': 'chills',
    'shivering': 'shivering',
    'shivers': 'shivering',
    'sweating': 'sweating',
    'profuse sweating': 'sweating',
    'night sweats': 'sweating',
    'dehydration': 'dehydration',
    'loss of appetite': 'loss_of_appetite',
    'poor appetite': 'loss_of_appetite',
    'reduced appetite': 'loss_of_appetite',
    'increased appetite': 'increased_appetite',
    'excessive hunger': 'excessive_hunger',
    'weight loss': 'weight_loss',
    'losing weight': 'weight_loss',
    'weight gain': 'weight_gain',
    'gaining weight': 'weight_gain',
    'dizziness': 'dizziness',
    'dizzy': 'dizziness',
    'giddy': 'dizziness',
    'loss of balance': 'loss_of_balance',
    'unsteadiness': 'unsteadiness',
    'spinning movements': 'spinning_movements',
    'vertigo': 'spinning_movements',
    'fast heart rate': 'fast_heart_rate',
    'palpitations': 'palpitations',
    'irregular heartbeat': 'palpitations',
    'restlessness': 'restlessness',
    'anxiety': 'anxiety',
    'depression': 'depression',
    'mood swings': 'mood_swings',
    'irritability': 'irritability',
    'malaise': 'malaise',

    # Dermatological / Skin
    'itching': 'itching',
    'itchy': 'itching',
    'itchiness': 'itching',
    'skin rash': 'skin_rash',
    'rash': 'skin_rash',
    'rashes': 'skin_rash',
    'red spots': 'red_spots_over_body',
    'red spots over body': 'red_spots_over_body',
    'nodal skin eruptions': 'nodal_skin_eruptions',
    'skin eruptions': 'nodal_skin_eruptions',
    'acne': 'pus_filled_pimples',
    'pimples': 'pus_filled_pimples',
    'pus filled pimples': 'pus_filled_pimples',
    'blackheads': 'blackheads',
    'blister': 'blister',
    'blisters': 'blister',
    'skin peeling': 'skin_peeling',
    'scabs': 'yellow_crust_ooze',
    'yellow crust ooze': 'yellow_crust_ooze',
    'red sore around nose': 'red_sore_around_nose',
    'yellowish skin': 'yellowish_skin',
    'yellow skin': 'yellowish_skin',
    'jaundice': 'yellowish_skin',
    'bruising': 'bruising',
    'bruises': 'bruising',

    # Urinary & Renal
    'burning urination': 'burning_micturition',
    'burning micturition': 'burning_micturition',
    'painful urination': 'burning_micturition',
    'burning while peeing': 'burning_micturition',
    'dark urine': 'dark_urine',
    'yellow urine': 'yellow_urine',
    'frequent urination': 'polyuria',
    'polyuria': 'polyuria',
    'continuous feel of urine': 'continuous_feel_of_urine',
    'bladder discomfort': 'bladder_discomfort',
    'foul smell of urine': 'foul_smell_of urine',
    'spotting urination': 'spotting_ urination',

    # Eyes & Vision
    'yellowing of eyes': 'yellowing_of_eyes',
    'yellow eyes': 'yellowing_of_eyes',
    'redness of eyes': 'redness_of_eyes',
    'red eyes': 'redness_of_eyes',
    'sunken eyes': 'sunken_eyes',
    'watering from eyes': 'watering_from_eyes',
    'watery eyes': 'watering_from_eyes',
    'blurred and distorted vision': 'blurred_and_distorted_vision',
    'blurred vision': 'blurred_and_distorted_vision',
    'blurry vision': 'blurred_and_distorted_vision',
    'visual disturbances': 'visual_disturbances',

    # Mouth & ENT
    'loss of smell': 'loss_of_smell',
    'cannot smell': 'loss_of_smell',
    'ulcers on tongue': 'ulcers_on_tongue',
    'mouth ulcers': 'ulcers_on_tongue',
    'patches in throat': 'patches_in_throat',
    'slurred speech': 'slurred_speech'
}

# Auto-register literal dataset symptom names and their spaced equivalents into synonym map
for symptom in DATASET_SYMPTOMS:
    cleaned_phrase = symptom.replace('_', ' ').strip().lower()
    if cleaned_phrase not in SYNONYM_MAP:
        SYNONYM_MAP[cleaned_phrase] = symptom
    if symptom.lower() not in SYNONYM_MAP:
        SYNONYM_MAP[symptom.lower()] = symptom

# Sort multi-word phrases by descending length for greedy matching
MULTI_WORD_PHRASES = sorted(
    [k for k in SYNONYM_MAP.keys() if ' ' in k],
    key=lambda s: len(s),
    reverse=True
)


def extract_symptoms(text):
    """
    Takes conversational patient text and extracts canonical symptom keys matching
    the ML model's 132 features.
    
    Steps:
    1. Multi-word phrase matching against synonyms and clinical features.
    2. NLTK tokenization and stopword removal.
    3. Single-word token matching.
    4. Validation against master 132-symptom vocabulary.
    """
    if not text or not str(text).strip():
        return []

    text_lower = str(text).lower()
    # Normalize punctuation into whitespace for smooth matching
    normalized_text = re.sub(r'[,.;:!?/()]+', ' ', text_lower)
    normalized_text = f" {normalized_text} "

    found_symptoms = set()

    # Step 1: Greedy multi-word phrase matching
    for phrase in MULTI_WORD_PHRASES:
        pattern = r'(?:\b)' + re.escape(phrase) + r'(?:\b)'
        if re.search(pattern, normalized_text):
            canonical = SYNONYM_MAP[phrase]
            found_symptoms.add(canonical)
            # Replace matched phrase to avoid redundant sub-token matches
            normalized_text = re.sub(pattern, ' ', normalized_text)

    # Step 2: NLTK tokenization
    try:
        tokens = word_tokenize(normalized_text)
    except Exception:
        tokens = normalized_text.split()

    # Step 3: Remove stopwords and non-alphabetical tokens
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'you', 'he', 'she', 'it', 'they', 'a', 'an', 'the', 'and', 'or', 'is', 'was', 'am', 'are', 'in', 'on', 'with', 'from', 'at', 'have', 'had', 'has', 'feel', 'feeling', 'since', 'yesterday', 'today'}

    filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words]

    # Step 4: Single-word lookup in synonym map
    for word in filtered_tokens:
        if word in SYNONYM_MAP:
            found_symptoms.add(SYNONYM_MAP[word])

    # Filter to only valid dataset symptoms if vocabulary is loaded
    if DATASET_SYMPTOMS:
        final_symptoms = [s for s in found_symptoms if s in DATASET_SYMPTOMS]
    else:
        final_symptoms = list(found_symptoms)

    return sorted(list(set(final_symptoms)))


def format_symptom_display_name(symptom_code):
    """
    Formats a raw dataset symptom column (e.g., 'high_fever', 'burning_micturition')
    into a patient-friendly readable title (e.g., 'High Fever', 'Burning Urination').
    """
    if not symptom_code:
        return ""
    
    # Specific clinical replacements for better patient readability
    custom_labels = {
        'burning_micturition': 'Burning Urination',
        'continuous_sneezing': 'Continuous Sneezing',
        'spotting_ urination': 'Spotting Urination',
        'foul_smell_of urine': 'Foul Smelling Urine',
        'continuous_feel_of_urine': 'Frequent Urge to Urinate',
        'polyuria': 'Frequent Urination',
        'distention_of_abdomen': 'Abdominal Bloating',
        'swelled_lymph_nodes': 'Swollen Lymph Nodes',
        'pain_behind_the_eyes': 'Pain Behind the Eyes',
        'passage_of_gases': 'Gas / Flatulence',
        'toxic_look_(typhos)': 'High Toxic Fever Appearance',
        'dischromic _patches': 'Discolored Skin Patches',
        'fluid_overload.1': 'Fluid Retention'
    }

    if symptom_code in custom_labels:
        return custom_labels[symptom_code]

    # Default: replace underscores, clean spaces, title-case
    clean = symptom_code.replace('_', ' ').strip()
    return clean.title()