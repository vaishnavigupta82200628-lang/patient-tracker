import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ==========================================
# KNOWN SYMPTOM KEYWORDS DATABASE
# ==========================================
# This is our reference list. In a real production system, this could
# come from a medical database. For our project, we define common symptoms.

SYMPTOM_KEYWORDS = [
    # General
    'fever', 'headache', 'fatigue', 'weakness', 'chills', 'sweating',
    'dizziness', 'weight loss', 'loss of appetite', 'insomnia', 'anxiety',

    # Respiratory
    'cough', 'cold', 'sore throat', 'runny nose', 'sneezing',
    'shortness of breath', 'difficulty breathing', 'chest pain',

    # Digestive
    'nausea', 'vomiting', 'diarrhea', 'constipation', 'stomach pain',
    'abdominal pain', 'bloating', 'acidity', 'indigestion',

    # Pain
    'body pain', 'joint pain', 'muscle pain', 'back pain', 'neck pain',
    'ear pain', 'eye pain', 'toothache',

    # Skin / Dermatology
    'acne', 'pimples', 'oily skin', 'dry skin', 'blackheads', 'whiteheads',
    'rash', 'itching', 'swelling', 'redness', 'dark spots', 'skin irritation',
    'acne marks', 'scars', 'inflammation',

    # Vision / Eyes
    'blurred vision', 'sore eyes', 'red eyes', 'watery eyes',

    # Other
    'hair loss', 'dandruff'
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
    found_symptoms = set()  # using a set to avoid duplicates

    # Step 1: Check for multi-word symptoms first (e.g. "sore throat", "body pain")
    # We check these against the raw lowercased text since they're phrases.
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