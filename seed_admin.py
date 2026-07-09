"""
Run this script ONCE to create the first Admin account.
Usage: python seed_admin.py
"""
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    existing_admin = User.query.filter_by(email='admin@patienttracker.com').first()

    if existing_admin:
        print("⚠️  Admin already exists. No action taken.")
    else:
        admin = User(
            name='System Admin',
            email='admin@patienttracker.com',
            role='admin'
        )
        admin.set_password('Admin@123')  # Change this after first login!
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created successfully!")
        print("   Email: admin@patienttracker.com")
        print("   Password: Admin@123")