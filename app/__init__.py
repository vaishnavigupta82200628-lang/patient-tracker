from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from app import models

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.admin.routes import admin_bp
    from app.doctor.routes import doctor_bp
    from app.patient.routes import patient_bp
    from app.api.routes import api_bp 
    from app.notifications.routes import notifications_bp  # ← NEW
    from app.radiology.routes import radiology_bp
    from app.radiologist.routes import radiologist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(api_bp) 
    app.register_blueprint(notifications_bp)  
    app.register_blueprint(radiology_bp)
    app.register_blueprint(radiologist_bp)     # ← NEW

    with app.app_context():
        db.create_all()

    return app