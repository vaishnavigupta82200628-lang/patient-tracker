import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this-later'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'patient_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Radiology Module Config
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH = r'C:\poppler\poppler-26.02.0\Library\bin'
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'prescriptions')
    MAX_UPLOAD_SIZE_MB = 10