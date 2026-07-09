import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key is used to sign session cookies securely.
    # In production, this should come from an environment variable, never hardcoded.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this-later'

    # Database file will be stored inside the 'instance' folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'patient_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False