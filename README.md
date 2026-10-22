# 🏥 Patient Tracker — AI Powered Hospital Management System

A full-stack, AI-powered hospital management platform built for Smart India Hackathon, featuring role-based dashboards, an NLP-driven symptom checker, ML-based disease prediction, and a complete Radiology Appointment & Diagnostic Test Booking module.

---

## ✨ Features

### Core Hospital Management
- 🔐 **Authentication & RBAC** — Secure login/register with role-based access control (Admin, Doctor, Patient, Radiologist)
- 📊 **Role-Based Dashboards** — Dedicated dashboards with real-time stats for each user role
- 📅 **Appointment System** — Booking, approval workflow, doctor search/filter
- 📋 **Medical Records** — Digital record-keeping tied to completed appointments
- 🤖 **AI Symptom Analyzer** — NLP-based symptom extraction using NLTK (150+ recognized symptoms)
- 🧠 **ML Disease Prediction** — scikit-learn Naive Bayes classifier trained on 23 diseases, with confidence scores and plain-language explanations
- 🔌 **REST API** — Versioned JSON API (`/api/v1/...`) powering charts and future integrations
- 📈 **Interactive Charts** — Chart.js-powered analytics on dashboards
- 📄 **PDF Reports** — Downloadable medical records and appointment summaries (ReportLab)
- 📥 **CSV Export** — Bulk data export for admins and doctors
- 🔔 **Notifications** — Real-time in-app alerts for appointments and records
- ⭐ **Ratings & Reviews** — Patients rate doctors after completed visits
- 🌗 **Dark Mode** — Persistent theme toggle
- 🔑 **Change Password** — Secure self-service password management

### Radiology Appointment & Diagnostic Test Booking Module
- 📷 **Test Booking** — MRI, CT Scan, X-Ray, Ultrasound, Mammography, Doppler, PET Scan, Fluoroscopy, Interventional Radiology
- 📤 **Prescription Upload + OCR** — Tesseract OCR automatically validates prescriptions against diagnostic keywords
- 💳 **Simulated Payment & Invoicing** — Realistic payment flow with auto-generated booking IDs and invoices
- 🩺 **Admin Approval Workflow** — Review, approve/reject, and assign machine/radiologist/room/slot
- 👨‍⚕️ **Radiologist Panel** — View assigned scans and upload findings
- 📍 **Progress Tracking** — Visual timeline from request to report-ready, with QR code and PDF receipts

### Analytics Dashboard
- 💰 Revenue trends (monthly)
- 📊 Top predicted diseases (from AI Symptom Checker logs)
- 🏆 Top-rated doctors leaderboard

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | Python, Flask (Blueprints, App Factory pattern) |
| Database | SQLite, SQLAlchemy ORM |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Authentication | Flask-Login, Werkzeug (password hashing) |
| AI / NLP | NLTK |
| Machine Learning | scikit-learn (Multinomial Naive Bayes) |
| OCR | Tesseract OCR, pdf2image, Poppler |
| Charts | Chart.js |
| Documents | ReportLab (PDF), Python `csv`, `qrcode` |
| Forms | Flask-WTF |

---

## 📁 Project Structure

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed locally
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) installed locally

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd patient-tracker

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Update Tesseract/Poppler paths in config.py to match your local installation

# Seed initial data
python seed_admin.py
python seed_radiology_data.py

# Train the ML disease prediction model
python app/ai/train_model.py

# Run the application
python run.py
```

Visit `http://127.0.0.1:5000` in your browser.

### Default Admin Login

*(Change this immediately after first login.)*

---

## 🔐 Security Highlights
- Passwords hashed with Werkzeug (never stored in plaintext)
- Role-based access control enforced on every protected route
- Ownership checks to prevent unauthorized data access (IDOR protection)
- Secure file uploads with UUID filenames, extension whitelisting, and size limits
- CSRF protection via Flask-WTF on all forms
- Server-side validation on every input, regardless of client-side checks

---

## 📄 License
Built for academic and hackathon purposes as part of Smart India Hackathon.

---

## 🙏 Acknowledgements
Developed as a B.Voc AI & Robotics project, demonstrating full-stack development, applied AI/ML, and secure software engineering practices.
