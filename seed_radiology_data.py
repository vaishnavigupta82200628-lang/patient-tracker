"""
Run this script ONCE to populate diagnostic tests and machines.
Usage: python seed_radiology_data.py
"""
from app import create_app
from app.extensions import db
from app.models import DiagnosticTest, Machine

app = create_app()

with app.app_context():
    # ---- Diagnostic Tests ----
    tests_data = [
        {
            "name": "MRI",
            "category": "Imaging",
            "base_price": 4500.0,
            "preparation_instructions": "Remove all metal objects. Reach 30 minutes early. Bring previous reports if any."
        },
        {
            "name": "CT Scan",
            "category": "Imaging",
            "base_price": 3500.0,
            "preparation_instructions": "Fasting for 4 hours before the scan. Drink water as instructed. Bring your creatinine report."
        },
        {
            "name": "X-Ray",
            "category": "Imaging",
            "base_price": 500.0,
            "preparation_instructions": "No special preparation needed. Remove jewelry from the area being scanned."
        },
        {
            "name": "Ultrasound",
            "category": "Imaging",
            "base_price": 1200.0,
            "preparation_instructions": "Full bladder may be required depending on the type of scan. Follow doctor's specific instructions."
        },
        {
            "name": "Mammography",
            "category": "Imaging",
            "base_price": 2000.0,
            "preparation_instructions": "Avoid using deodorant or powder on the day of the test. Schedule outside your menstrual period if possible."
        },
        {
            "name": "Doppler",
            "category": "Imaging",
            "base_price": 1800.0,
            "preparation_instructions": "No special preparation needed for most Doppler studies."
        },
        {
            "name": "PET Scan",
            "category": "Nuclear Medicine",
            "base_price": 15000.0,
            "preparation_instructions": "Fasting for 6 hours before the scan. Avoid strenuous exercise 24 hours prior. Inform staff if diabetic."
        },
        {
            "name": "Fluoroscopy",
            "category": "Imaging",
            "base_price": 2500.0,
            "preparation_instructions": "Fasting may be required. Follow specific instructions provided by your doctor."
        },
        {
            "name": "Interventional Radiology Procedure",
            "category": "Procedure",
            "base_price": 8000.0,
            "preparation_instructions": "Fasting required. Pre-procedure blood tests may be needed. Arrange for someone to accompany you home."
        },
    ]

    for t in tests_data:
        existing = DiagnosticTest.query.filter_by(name=t["name"]).first()
        if not existing:
            db.session.add(DiagnosticTest(**t))

    # ---- Machines ----
    machines_data = [
        {"name": "MRI Machine 1", "test_type": "MRI", "room_number": "201"},
        {"name": "MRI Machine 2", "test_type": "MRI", "room_number": "202"},
        {"name": "CT Scanner 1", "test_type": "CT Scan", "room_number": "105"},
        {"name": "X-Ray Unit 1", "test_type": "X-Ray", "room_number": "101"},
        {"name": "Ultrasound Unit 1", "test_type": "Ultrasound", "room_number": "110"},
        {"name": "Mammography Unit 1", "test_type": "Mammography", "room_number": "115"},
    ]

    for m in machines_data:
        existing = Machine.query.filter_by(name=m["name"]).first()
        if not existing:
            db.session.add(Machine(**m))

    db.session.commit()
    print("✅ Radiology master data seeded successfully!")
    print(f"   Diagnostic Tests: {DiagnosticTest.query.count()}")
    print(f"   Machines: {Machine.query.count()}")