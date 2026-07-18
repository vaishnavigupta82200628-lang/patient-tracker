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
