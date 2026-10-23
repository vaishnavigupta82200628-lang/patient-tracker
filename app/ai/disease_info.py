"""
Comprehensive medical reference metadata for all 41 diseases predicted by our clinical ML model.
Provides patient-friendly clinical summaries and recommended medical doctor specializations
to guide timely specialist consultations.
"""

# Master reference database for all 41 disease classes
DISEASE_DETAILS = {
    "(vertigo) Paroymsal  Positional Vertigo": {
        "description": "A disorder of the inner ear causing brief episodes of mild to intense dizziness or spinning sensations triggered by changes in head position.",
        "specialization": "ENT Specialist"
    },
    "AIDS": {
        "description": "Acquired Immunodeficiency Syndrome is a chronic, potentially life-threatening condition caused by the human immunodeficiency virus (HIV), impacting the immune system.",
        "specialization": "Infectious Disease Specialist"
    },
    "Acne": {
        "description": "A common dermatological condition where hair follicles become clogged with excess sebum and dead skin cells, causing pimples, blackheads, and inflammation.",
        "specialization": "Dermatologist"
    },
    "Alcoholic hepatitis": {
        "description": "Severe inflammation and injury of the liver parenchyma caused by prolonged, heavy alcohol consumption, leading to jaundice, swelling, and abdominal pain.",
        "specialization": "Gastroenterologist"
    },
    "Allergy": {
        "description": "An exaggerated immune response to normally harmless environmental substances, leading to skin irritation, sneezing, urticaria, or mucosal inflammation.",
        "specialization": "Allergist / Immunologist"
    },
    "Arthritis": {
        "description": "Acute or chronic inflammation of one or more joints, causing pain, swelling, stiffness, and reduced range of motion that often worsens with activity.",
        "specialization": "Rheumatologist"
    },
    "Bronchial Asthma": {
        "description": "A chronic inflammatory disorder of the airways causing recurrent episodes of wheezing, breathlessness, chest tightness, and nighttime coughing.",
        "specialization": "Pulmonologist"
    },
    "Cervical spondylosis": {
        "description": "Age-related wear and degeneration of the cervical spine vertebrae and intervertebral discs, causing chronic neck stiffness, localized pain, and radiating numbness.",
        "specialization": "Orthopedic Surgeon"
    },
    "Chicken pox": {
        "description": "A highly contagious viral infection caused by the varicella-zoster virus, causing an intensely itchy blister-like vesicular skin rash, fever, and malaise.",
        "specialization": "General Physician"
    },
    "Chronic cholestasis": {
        "description": "A prolonged hepatobiliary disorder where bile flow from the liver is obstructed or impaired, causing severe pruritus, dark urine, and jaundice.",
        "specialization": "Gastroenterologist"
    },
    "Common Cold": {
        "description": "A mild viral infection of the upper respiratory tract involving the nasal mucosa and throat, typically causing sneezing, nasal discharge, and congestion.",
        "specialization": "General Physician"
    },
    "Dengue": {
        "description": "A mosquito-borne flavivirus infection characterized by acute high fever, severe retro-orbital headache, debilitating joint and muscle pain, and petechial rash.",
        "specialization": "General Physician"
    },
    "Diabetes": {
        "description": "A chronic metabolic disorder characterized by elevated blood glucose levels resulting from defects in insulin secretion, insulin resistance, or both.",
        "specialization": "Endocrinologist"
    },
    "Dimorphic hemmorhoids(piles)": {
        "description": "Swollen and inflamed vascular cushions in the lower rectum and anus, causing rectal discomfort, anal itching, and painless rectal bleeding during defecation.",
        "specialization": "General Surgeon"
    },
    "Drug Reaction": {
        "description": "An unexpected adverse immunological or physiological reaction to a prescribed or over-the-counter pharmaceutical agent, manifesting as rashes, hives, or swelling.",
        "specialization": "Dermatologist"
    },
    "Fungal infection": {
        "description": "A superficial mycotic infection affecting the epidermis, nails, or mucosal membranes, causing itching, skin peeling, erythema, and circular scaly lesions.",
        "specialization": "Dermatologist"
    },
    "GERD": {
        "description": "Gastroesophageal Reflux Disease occurs when stomach acid frequently flows back into the esophagus, causing persistent heartburn, acid regurgitation, and chest discomfort.",
        "specialization": "Gastroenterologist"
    },
    "Gastroenteritis": {
        "description": "Acute inflammation of the gastric and intestinal mucosa, commonly called stomach flu, causing watery diarrhea, abdominal cramping, nausea, and vomiting.",
        "specialization": "General Physician"
    },
    "Heart attack": {
        "description": "A critical cardiovascular emergency where coronary blood supply to heart muscle is acutely interrupted, causing crushing retrosternal chest pain, radiating arm pain, and dyspnea.",
        "specialization": "Cardiologist"
    },
    "Hepatitis B": {
        "description": "A viral infection that attacks the liver and can cause both acute and chronic disease, transmitted through contact with infected blood or bodily fluids.",
        "specialization": "Gastroenterologist"
    },
    "Hepatitis C": {
        "description": "A blood-borne viral infection causing chronic inflammation of liver tissue, often asymptomatic in early stages but potentially leading to cirrhosis if untreated.",
        "specialization": "Gastroenterologist"
    },
    "Hepatitis D": {
        "description": "A serious liver infection caused by the hepatitis delta virus that relies on concurrent hepatitis B infection to replicate, accelerating liver pathology.",
        "specialization": "Gastroenterologist"
    },
    "Hepatitis E": {
        "description": "An enterically transmitted viral liver disease typically spread through contaminated drinking water, presenting with jaundice, loss of appetite, and nausea.",
        "specialization": "Gastroenterologist"
    },
    "Hypertension": {
        "description": "Persistent elevation of systemic arterial blood pressure, which increases the workload on the heart and vasculature, often presenting with occasional headaches.",
        "specialization": "Cardiologist"
    },
    "Hyperthyroidism": {
        "description": "A metabolic state resulting from excessive production of thyroid hormones, causing unexplained weight loss, tachycardia, heat intolerance, tremor, and nervousness.",
        "specialization": "Endocrinologist"
    },
    "Hypoglycemia": {
        "description": "An acute clinical condition caused by abnormally low blood plasma glucose concentrations, leading to tremors, diaphoresis, dizziness, tachycardia, and mental confusion.",
        "specialization": "Endocrinologist"
    },
    "Hypothyroidism": {
        "description": "A common endocrine condition where the thyroid gland is underactive and produces insufficient thyroid hormone, leading to chronic fatigue, weight gain, and cold intolerance.",
        "specialization": "Endocrinologist"
    },
    "Impetigo": {
        "description": "A superficial bacterial skin infection, common in children, presenting with erythematous lesions that erupt, weep, and form distinctive honey-colored crusts.",
        "specialization": "Dermatologist"
    },
    "Jaundice": {
        "description": "Yellowish staining of the skin, sclera, and mucous membranes caused by hyperbilirubinemia, indicating hepatic, biliary, or hemolytic dysfunction.",
        "specialization": "Gastroenterologist"
    },
    "Malaria": {
        "description": "A life-threatening protozoan infection transmitted through female Anopheles mosquito bites, causing cyclical paroxysms of high fever, rigors, and profuse sweating.",
        "specialization": "General Physician"
    },
    "Migraine": {
        "description": "A recurrent neurological disorder causing moderate-to-severe throbbing unilateral headaches, typically accompanied by photophobia, phonophobia, and nausea.",
        "specialization": "Neurologist"
    },
    "Osteoarthristis": {
        "description": "A degenerative wear-and-tear arthritis resulting from progressive breakdown of joint cartilage and underlying bone, causing joint stiffness and localized mechanical pain.",
        "specialization": "Orthopedic Surgeon"
    },
    "Paralysis (brain hemorrhage)": {
        "description": "Acute loss of motor function and sensation in voluntary muscle groups caused by intracranial vascular rupture or intracerebral hemorrhage, requiring urgent neurosurgical intervention.",
        "specialization": "Neurologist"
    },
    "Peptic ulcer diseae": {
        "description": "Focal mucosal defects and open sores in the protective lining of the stomach or duodenum, causing burning epigastric discomfort, indigestion, and bloating.",
        "specialization": "Gastroenterologist"
    },
    "Pneumonia": {
        "description": "An acute lower respiratory infection causing inflammation of the pulmonary alveoli, which fill with exudate, presenting with productive cough, fever, rigors, and dyspnea.",
        "specialization": "Pulmonologist"
    },
    "Psoriasis": {
        "description": "An autoimmune, chronic dermatological disease causing hyperproliferation of keratinocytes, resulting in demarcated erythematous plaques with adherent silvery scales.",
        "specialization": "Dermatologist"
    },
    "Tuberculosis": {
        "description": "A chronic infectious granulomatous disease caused by Mycobacterium tuberculosis, primarily involving the lungs and presenting with prolonged cough, hemoptysis, fever, and weight loss.",
        "specialization": "Pulmonologist"
    },
    "Typhoid": {
        "description": "A systemic salmonellosis infection caused by Salmonella enterica serotype Typhi, presenting with step-ladder fever, headache, anorexia, abdominal pain, and hepatosplenomegaly.",
        "specialization": "General Physician"
    },
    "Urinary tract infection": {
        "description": "An infection of the urinary system (cystitis or pyelonephritis), typically characterized by dysuria, urinary frequency, urgency, suprapubic discomfort, and cloudy urine.",
        "specialization": "Urologist"
    },
    "Varicose veins": {
        "description": "Subcutaneous, dilated, tortuous veins in the lower extremities resulting from incompetent venous valves, causing aching heaviness, edema, and venous stasis changes.",
        "specialization": "Vascular Surgeon"
    },
    "hepatitis A": {
        "description": "An acute viral liver infection transmitted via the fecal-oral route, causing fatigue, nausea, abdominal discomfort, dark urine, and transient jaundice.",
        "specialization": "Gastroenterologist"
    }
}

# Add normalized aliases for trailing whitespace versions found in raw datasets
DISEASE_DETAILS["Diabetes "] = DISEASE_DETAILS["Diabetes"]
DISEASE_DETAILS["Hypertension "] = DISEASE_DETAILS["Hypertension"]


class DiseaseInfoProxy(dict):
    """
    Dictionary proxy that maintains 100% backward compatibility for legacy
    code accessing DISEASE_INFO as a {disease: description} dict, while also
    supporting rich attribute/metadata lookup.
    """
    def __init__(self, data):
        super().__init__()
        for disease, info in data.items():
            self[disease] = info["description"]

    def get_details(self, disease_name):
        canonical = disease_name.strip() if disease_name else ""
        return DISEASE_DETAILS.get(canonical) or DISEASE_DETAILS.get(disease_name) or {
            "description": "No detailed clinical description available.",
            "specialization": "General Physician"
        }

    def get_description(self, disease_name):
        return self.get_details(disease_name)["description"]

    def get_specialization(self, disease_name):
        return self.get_details(disease_name)["specialization"]


# Backward-compatible global dictionary object
DISEASE_INFO = DiseaseInfoProxy(DISEASE_DETAILS)


def get_disease_description(disease_name):
    """Returns patient-friendly clinical description."""
    return DISEASE_INFO.get_description(disease_name)


def get_recommended_specialization(disease_name):
    """Returns recommended medical doctor specialization."""
    return DISEASE_INFO.get_specialization(disease_name)