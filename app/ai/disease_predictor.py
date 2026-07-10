import pickle
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(current_dir, 'model')

# Load the trained model and vectorizer once when this module is imported
with open(os.path.join(model_dir, 'disease_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(model_dir, 'vectorizer.pkl'), 'rb') as f:
    vectorizer = pickle.load(f)


def predict_disease(symptoms_list):
    """
    Takes a list of symptom strings (e.g. ['fever', 'headache', 'body pain'])
    and returns (predicted_disease, confidence_percentage).
    """
    if not symptoms_list:
        return None, 0.0

    # Convert symptoms list to underscore-joined format matching our training data
    symptoms_text = ' '.join([s.replace(' ', '_') for s in symptoms_list])

    # Vectorize the input using the SAME vectorizer used in training
    vectorized_input = vectorizer.transform([symptoms_text])

    # Predict the disease
    predicted_disease = model.predict(vectorized_input)[0]

    # Get confidence score (probability of the predicted class)
    probabilities = model.predict_proba(vectorized_input)[0]
    confidence = max(probabilities) * 100

    return predicted_disease, round(confidence, 2)