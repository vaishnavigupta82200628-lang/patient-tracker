import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ==========================================
# KNOWN SYMPTOM KEYWORDS DATABASE (150+ symptoms, categorized)
# ==========================================

SYMPTOM_KEYWORDS = [
    # General
    'fever', 'high fever', 'mild fever', 'headache', 'severe headache', 'fatigue',
    'weakness', 'chills', 'sweating', 'night sweats', 'dizziness', 'weight loss',
    'weight gain', 'loss of appetite', 'increased appetite', 'insomnia', 'anxiety',
    'restlessness', 'excessive thirst', 'frequent urination', 'malaise', 'lethargy',
    'drowsiness', 'confusion', 'dehydration', 'pale skin', 'cold sweats', 'hot flashes',
    'hunger pangs', 'excessive hunger', 'numbness', 'tingling sensation', 'muscle weakness',
    'swollen glands', 'swollen lymph nodes', 'sensitivity to cold', 'sensitivity to heat',

    # Respiratory
    'cough', 'dry cough', 'wet cough', 'cold', 'sore throat', 'runny nose', 'blocked nose',
    'nasal congestion', 'sneezing', 'shortness of breath', 'difficulty breathing', 'wheezing',
    'chest pain', 'chest tightness', 'congestion', 'hoarseness', 'difficulty swallowing',

    # Digestive
    'nausea', 'vomiting', 'diarrhea', 'constipation', 'stomach pain', 'abdominal pain',
    'bloating', 'acidity', 'indigestion', 'heartburn', 'loss of taste', 'loss of smell',
    'blood in stool', 'gas', 'cramps', 'stomach cramps', 'upset stomach', 'dry mouth',
    'excessive salivation', 'mouth ulcers', 'bad breath',

    # Pain
    'body pain', 'joint pain', 'muscle pain', 'back pain', 'neck pain', 'ear pain',
    'eye pain', 'toothache', 'stiffness', 'leg pain', 'shoulder pain', 'knee pain',

    # Skin
    'acne', 'pimples', 'oily skin', 'dry skin', 'blackheads', 'whiteheads', 'rash',
    'itching', 'swelling', 'redness', 'dark spots', 'skin irritation', 'acne marks',
    'scars', 'inflammation', 'dandruff', 'hair loss', 'hives', 'dry patches',
    'flaky skin', 'jaundice', 'dark circles',

    # Eyes
    'blurred vision', 'sore eyes', 'red eyes', 'watery eyes', 'itchy eyes',
    'eye discharge', 'sensitivity to light', 'dry eyes',

    # Urinary
    'burning urination', 'painful urination', 'cloudy urine', 'pelvic pain',
    'lower abdominal pain', 'dark urine',

    # Cardiac / Circulatory
    'palpitations', 'high blood pressure', 'low blood pressure', 'irregular heartbeat',
    'fainting', 'cold hands', 'cold feet',

    # Mental / Sleep
    'mood swings', 'difficulty concentrating', 'irritability', 'nervousness', 'panic',
    'trouble sleeping', 'nightmares', 'excessive worry',

    # Ear / Nose / Throat
    'hearing loss', 'ringing in ears', 'nose bleed',

    # Infection-related patterns
    'red spots on skin', 'bleeding gums', 'yellowing of skin',
]

# Separate single-word and multi-word symptoms for different matching strategies
MULTI_WORD_SYMPTOMS = [s for s in SYMPTOM_KEYWORDS if ' ' in s]
SINGLE_WORD_SYMPTOMS = [s for s in SYMPTOM_KEYWORDS if ' ' not in s]


def extract_symptoms(text):
    """
    Takes raw patient text input and returns a list of matched symptoms.
    Uses NLTK for tokenization and stopword removal.
    """
    if not text or not text.strip():
        return []

    text_lower = text.lower()
    found_symptoms = set()

    # Step 1: Check for multi-word symptoms first (phrase-level match on raw text)
    for phrase in MULTI_WORD_SYMPTOMS:
        if phrase in text_lower:
            found_symptoms.add(phrase)

    # Step 2: Tokenize the text into individual words
    tokens = word_tokenize(text_lower)

    # Step 3: Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [
        word for word in tokens
        if word.isalpha() and word not in stop_words
    ]

    # Step 4: Check single-word tokens against our single-word symptom list
    for word in filtered_tokens:
        if word in SINGLE_WORD_SYMPTOMS:
            found_symptoms.add(word)

    return sorted(list(found_symptoms))