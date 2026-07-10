"""
This script trains our disease prediction model.
Run it ONCE (or whenever you update the training data): python app/ai/train_model.py
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
# TRAINING DATA
# ==========================================
# Format: symptoms (space-separated keywords) -> disease label
# In a real production system, this would come from a large medical dataset.
# For our hackathon project, we define a curated, realistic dataset.

training_data = [
    ("fever cough cold sore_throat", "Common Cold"),
    ("fever cough runny_nose sneezing", "Common Cold"),
    ("cold sneezing runny_nose", "Common Cold"),

    ("fever body_pain headache fatigue chills", "Flu"),
    ("fever body_pain weakness chills sweating", "Flu"),
    ("high_fever body_pain headache fatigue", "Flu"),

    ("headache dizziness blurred_vision", "Migraine"),
    ("headache nausea sensitivity_to_light", "Migraine"),
    ("severe_headache dizziness nausea", "Migraine"),

    ("acne pimples oily_skin blackheads", "Acne"),
    ("pimples whiteheads blackheads oily_skin", "Acne"),
    ("acne_marks pimples inflammation skin_irritation", "Acne"),

    ("stomach_pain nausea vomiting diarrhea", "Food Poisoning"),
    ("abdominal_pain vomiting diarrhea nausea", "Food Poisoning"),
    ("stomach_pain diarrhea vomiting fever", "Food Poisoning"),

    ("chest_pain shortness_of_breath difficulty_breathing", "Respiratory Issue"),
    ("cough chest_pain difficulty_breathing", "Respiratory Issue"),
    ("shortness_of_breath wheezing chest_pain", "Respiratory Issue"),

    ("joint_pain swelling muscle_pain stiffness", "Arthritis"),
    ("joint_pain swelling back_pain", "Arthritis"),

    ("itching rash redness swelling", "Allergic Reaction"),
    ("rash itching skin_irritation swelling", "Allergic Reaction"),
    ("sneezing itching watery_eyes rash", "Allergic Reaction"),

    ("fatigue weakness loss_of_appetite weight_loss", "Anemia"),
    ("fatigue dizziness weakness pale_skin", "Anemia"),

    ("insomnia anxiety fatigue weakness", "Stress/Anxiety"),
    ("anxiety insomnia headache fatigue", "Stress/Anxiety"),
]

# ==========================================
# PREPARE DATA
# ==========================================
df = pd.DataFrame(training_data, columns=['symptoms', 'disease'])

X = df['symptoms']  # input features (symptom text)
y = df['disease']   # target labels (disease names)

# Split into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# VECTORIZE TEXT (convert words to numbers)
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
print(f"   Diseases covered: {sorted(y.unique())}")

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