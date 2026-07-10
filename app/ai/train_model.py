"""
This script trains our disease prediction model.
Run it whenever you update the training data: python app/ai/train_model.py
It saves two files: disease_model.pkl and vectorizer.pkl inside app/ai/model/
"""
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

# ==========================================
# TRAINING DATA (23 diseases, multiple examples each)
# ==========================================

training_data = [
    # Common Cold
    ("cough cold sore_throat runny_nose sneezing congestion", "Common Cold"),
    ("cold sneezing runny_nose blocked_nose cough", "Common Cold"),

    # Flu
    ("fever body_pain headache fatigue chills weakness", "Flu"),
    ("high_fever body_pain weakness chills sweating fatigue", "Flu"),

    # Migraine
    ("headache severe_headache dizziness blurred_vision sensitivity_to_light nausea", "Migraine"),
    ("severe_headache nausea dizziness sensitivity_to_light", "Migraine"),

    # Acne
    ("acne pimples oily_skin blackheads whiteheads acne_marks", "Acne"),
    ("pimples whiteheads blackheads oily_skin inflammation", "Acne"),

    # Food Poisoning
    ("stomach_pain vomiting diarrhea nausea abdominal_pain fever", "Food Poisoning"),
    ("abdominal_pain vomiting diarrhea nausea upset_stomach", "Food Poisoning"),

    # Asthma
    ("shortness_of_breath wheezing chest_tightness difficulty_breathing cough", "Asthma"),
    ("wheezing difficulty_breathing chest_tightness cough", "Asthma"),

    # Arthritis
    ("joint_pain swelling stiffness muscle_pain back_pain", "Arthritis"),
    ("joint_pain stiffness swelling knee_pain", "Arthritis"),

    # Allergic Reaction
    ("itching rash redness swelling sneezing watery_eyes", "Allergic Reaction"),
    ("rash itching skin_irritation swelling hives", "Allergic Reaction"),

    # Anemia
    ("fatigue weakness pale_skin dizziness shortness_of_breath", "Anemia"),
    ("weakness fatigue dizziness pale_skin", "Anemia"),

    # Stress/Anxiety
    ("anxiety insomnia restlessness irritability difficulty_concentrating", "Stress/Anxiety"),
    ("restlessness anxiety trouble_sleeping nervousness excessive_worry", "Stress/Anxiety"),

    # Typhoid
    ("fever abdominal_pain weakness loss_of_appetite headache constipation", "Typhoid"),
    ("high_fever weakness loss_of_appetite abdominal_pain", "Typhoid"),

    # Dengue
    ("high_fever joint_pain muscle_pain rash severe_headache fatigue", "Dengue"),
    ("fever rash joint_pain muscle_pain severe_headache", "Dengue"),

    # Malaria
    ("chills high_fever sweating headache nausea muscle_pain", "Malaria"),
    ("fever chills sweating headache weakness", "Malaria"),

    # Urinary Tract Infection
    ("burning_urination frequent_urination cloudy_urine lower_abdominal_pain fever", "Urinary Tract Infection"),
    ("painful_urination frequent_urination lower_abdominal_pain", "Urinary Tract Infection"),

    # Gastritis
    ("heartburn acidity indigestion stomach_pain bloating nausea", "Gastritis"),
    ("acidity indigestion bloating stomach_pain", "Gastritis"),

    # Conjunctivitis
    ("red_eyes itchy_eyes watery_eyes eye_discharge sensitivity_to_light", "Conjunctivitis"),
    ("red_eyes eye_discharge itchy_eyes", "Conjunctivitis"),

    # Sinusitis
    ("blocked_nose nasal_congestion headache sore_throat cough", "Sinusitis"),
    ("nasal_congestion headache blocked_nose", "Sinusitis"),

    # Bronchitis
    ("cough wet_cough chest_pain wheezing fatigue shortness_of_breath", "Bronchitis"),
    ("wet_cough chest_pain fatigue cough", "Bronchitis"),

    # Diabetes (Early Signs)
    ("excessive_thirst frequent_urination fatigue weight_loss blurred_vision", "Diabetes (Early Signs)"),
    ("frequent_urination excessive_thirst fatigue", "Diabetes (Early Signs)"),

    # Hypertension (Early Signs)
    ("headache dizziness chest_tightness palpitations fatigue", "Hypertension (Early Signs)"),
    ("dizziness headache palpitations", "Hypertension (Early Signs)"),

    # Eczema
    ("dry_skin itching redness rash flaky_skin inflammation", "Eczema"),
    ("dry_skin flaky_skin itching redness", "Eczema"),

    # Scalp Issue
    ("dandruff hair_loss itching dry_patches flaky_skin", "Scalp Issue"),
    ("dandruff itching hair_loss", "Scalp Issue"),

    # Sleep Disorder
    ("insomnia trouble_sleeping restlessness fatigue irritability difficulty_concentrating", "Sleep Disorder"),
    ("trouble_sleeping insomnia fatigue restlessness", "Sleep Disorder"),
]

# ==========================================
# PREPARE DATA
# ==========================================
df = pd.DataFrame(training_data, columns=['symptoms', 'disease'])
X = df['symptoms']
y = df['disease']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# VECTORIZE TEXT
# ==========================================
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# ==========================================
# TRAIN THE MODEL
# ==========================================
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# ==========================================
# EVALUATE MODEL
# ==========================================
predictions = model.predict(X_test_vectorized)
accuracy = accuracy_score(y_test, predictions)
print(f"✅ Model trained successfully!")
print(f"   Test Accuracy: {accuracy * 100:.2f}%")
print(f"   Training examples: {len(X_train)}")
print(f"   Testing examples: {len(X_test)}")
print(f"   Diseases covered ({len(y.unique())}): {sorted(y.unique())}")

# ==========================================
# SAVE MODEL AND VECTORIZER
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(current_dir, 'model')

with open(os.path.join(model_dir, 'disease_model.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(model_dir, 'vectorizer.pkl'), 'wb') as f:
    pickle.dump(vectorizer, f)

print(f"✅ Model saved to {model_dir}")