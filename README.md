# 🎓 UniSchedule — Smart Classroom & Timetable Scheduler

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)
![License](https://img.shields.io/badge/License-MIT-green)

**A full-stack university management platform with intelligent timetable generation, smart QR attendance, role-based dashboards, and an AI-powered chatbot.**

🌐 **Live Demo:** [smart-classroom-time-table-scheduler-1.onrender.com](https://smart-classroom-time-table-scheduler-1.onrender.com)

| Role | URL |
|------|-----|
| Login (all roles) | [/login](https://smart-classroom-time-table-scheduler-1.onrender.com/login) |
| Student Dashboard | [/student-app](https://smart-classroom-time-table-scheduler-1.onrender.com/student-app) |
| Faculty Dashboard | [/faculty-app](https://smart-classroom-time-table-scheduler-1.onrender.com/faculty-app) |

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Models](#-database-models)
- [Timetable Generation Algorithm](#-timetable-generation-algorithm)
- [Smart Attendance System](#-smart-attendance-system)
- [AI Chatbot](#-ai-chatbot)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Overview](#-api-overview)
- [Deployment](#-deployment-render)
- [Default Credentials](#-default-credentials)

---

## ✨ Features

### 🔐 Role-Based Access Control
- **Admin** — Full university management (departments, courses, faculty, students, classrooms)
- **Faculty** — Personal dashboard, timetable, attendance management, AI chatbot
- **Student** — Schedule viewer, attendance tracker, QR scanner, AI chatbot

### 📅 Intelligent Timetable Generator
- **Backtracking algorithm** with soft constraint scoring
- Hard constraints: no faculty/room/section double-booking, lunch slot reserved
- Soft constraints: difficulty-based slot preference, gap distribution, back-to-back day penalties
- Partial regeneration per department without disrupting others
- Post-generation validation with violation reports

### 📲 Smart Proxy-Proof Attendance
Multi-layer fraud detection for every attendance submission:

| # | Check | Detail |
|---|-------|--------|
| 1 | VPN Detection | Blocks known VPN/datacenter IP ranges (Cloudflare, NordVPN, AWS, etc.) |
| 2 | Active Session | Verifies faculty has started an attendance session |
| 3 | GPS Distance | Student must be within **100 m** of faculty (Haversine formula) |
| 4 | GPS Accuracy | Rejects if device GPS accuracy > 50 m |
| 5 | Rolling QR Token | Server-side tokens rotate every **3 seconds** |
| 6 | Section Enrollment | Confirms student is enrolled in that section |
| 7 | Face Verification | Selfie match against profile photo (flagging, not blocking) |
| 8 | Duplicate Guard | One submission per student per session |

### 🤖 AI Chatbot (Claude Powered)
- Separate AI assistants for Admin, Faculty, and Student roles
- Context-aware: knows the user's timetable, attendance, courses
- Suggests dashboard actions via structured `action` blocks
- Built on Anthropic's Claude API via OpenRouter

### 🔑 Password Reset via OTP
- 6-digit OTP sent to institutional email (`@srmap.edu.in`)
- OTP expires in 5 minutes
- Single-use reset token flow

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.1 |
| Database | SQLite (via Flask-SQLAlchemy + Flask-Migrate) |
| Auth | Session-based, Werkzeug password hashing |
| CSRF | Flask-WTF |
| AI | Anthropic Claude (via OpenRouter API) |
| Email | SMTP (Gmail / institutional SMTP) |
| Frontend | Vanilla HTML/CSS/JS (Jinja2 templates) |
| Deployment | Render.com |

---

## 📁 Project Structure

```
UniSchedule/
│
├── app.py                      # Flask app factory — registers blueprints, CSRF, DB
├── models.py                   # SQLAlchemy models (University, Faculty, Student, etc.)
├── timetable_generator.py      # Backtracking timetable algorithm
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
│
├── blueprints/
│   ├── auth.py                 # Login, logout, OTP password reset
│   ├── admin.py                # Admin dashboard routes
│   ├── faculty.py              # Faculty dashboard routes
│   ├── student.py              # Student dashboard routes
│   ├── api.py                  # REST API endpoints (CRUD for all entities)
│   ├── attendance.py           # Smart QR attendance system (7-layer validation)
│   ├── chatbot_admin.py        # Admin AI chatbot
│   ├── chatbot_faculty.py      # Faculty AI chatbot
│   ├── chatbot_student.py      # Student AI chatbot
│   ├── chatbot_utils.py        # Shared Claude API caller + formatters
│   └── utils.py                # login_required, role_required decorators, email sender
│
├── templates/
│   ├── base.html               # Base layout with navigation
│   ├── login.html              # Login page with OTP reset flow
│   ├── dashboard.html          # Admin dashboard
│   ├── faculty_dashboard.html  # Faculty full SPA dashboard
│   ├── student_dashboard.html  # Student full SPA dashboard
│   ├── attendance_faculty.html # Faculty QR session page
│   ├── attendance_student.html # Student QR scanner page
│   ├── timetable_*.html        # Timetable views (section, faculty, rooms, student)
│   └── ...                     # Other management pages
│
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   ├── uploads/faculty/        # Faculty profile photos
│   └── uploads/students/       # Student profile photos
│
├── migrations/                 # Flask-Migrate migration scripts
└── fixtures/                   # Seed data fixtures
```

---

## 🗄 Database Models

| Model | Description |
|-------|-------------|
| `University` | Global config: working days, timeslots, blocks, floors |
| `Department` | Academic departments with unique codes |
| `Course` | Courses with credits, difficulty, type (Theory/Lab), weekly frequency |
| `Faculty` | Faculty members with email, available slots, password hash, photo |
| `Student` | Students with UID, email, enrollment, photo |
| `Section` | Student groupings (A, B, C…) linked to department |
| `Classroom` | Rooms with block, floor, capacity, type (Theory/Lab) |
| `TimetableEntry` | Generated schedule: section × day × slot × course × faculty × room |
| `Attendance` | Per-student attendance records with date and status |
| `FacultyAbsence` | Faculty absence records with slots and reason |
| `PasswordResetToken` | OTP + secure reset token with expiry |

---

## ⚙️ Timetable Generation Algorithm

The algorithm (`timetable_generator.py`) uses a **backtracking search with soft constraint scoring**:

```
For each section:
  Sort courses: Hard > Medium > Easy (by difficulty, then credits)
  For each course × required_classes_per_week:
    Score all (day, slot) combinations:
      + Prefer early slots for Hard courses, late for Easy
      + Penalize back-to-back same-course days (+3)
      + Penalize adjacent slots (+2), reward gaps (-1)
      + Penalize Easy courses in morning prime slots (+2)
    Pick best slot respecting:
      ✗ Faculty already teaching
      ✗ Room already occupied
      ✗ Section already in class
      ✗ Lunch slot blocked
    If no slot found → backtrack up to 10 previous assignments
```

**Post-generation validation** checks for:
- Faculty double-booking
- Room double-booking  
- Section over-scheduling (> 6 classes/day)

---

## 📲 Smart Attendance System

### Faculty Flow
1. Navigate to **Attendance → Start Session**
2. Select course + section; GPS location is captured
3. A **rolling QR code** is displayed (refreshes every 3 seconds)
4. Live view shows present/absent count in real time
5. Click **Stop Session** → records committed to database

### Student Flow
1. Navigate to **Attendance → Scan QR**
2. Camera scans the QR code displayed by faculty
3. System validates: VPN check → GPS distance → QR token → enrollment → face selfie
4. Student receives instant confirmation (✓ Marked / error with reason)

### Manual Override
Faculty can also manually mark attendance via the roster view for any past date.

---

## 🤖 AI Chatbot

Each role has a dedicated chatbot endpoint powered by **Claude** (via OpenRouter):

| Role | Endpoint | Capabilities |
|------|----------|-------------|
| Student | `POST /api/chatbot/student` | Timetable lookup, attendance alerts, next class |
| Faculty | `POST /api/chatbot/faculty` | Teaching schedule, section attendance, workload |
| Admin | `POST /api/chatbot/admin` | University stats, department summaries, conflicts |

The chatbot is **context-aware** — it receives the user's full academic context (timetable, attendance, enrolled courses) as a system prompt before each conversation.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/harshavardhan1123/smart-classroom-and-time-table-generator.git
cd smart-classroom-and-time-table-generator
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables section below)
```

### 5. Initialize the database
```bash
flask db upgrade
# OR for fresh start (no migrations):
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
```

### 6. Run the application
```bash
python app.py
```

Visit `http://localhost:5001` in your browser.

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
# ── REQUIRED ──────────────────────────────────────────────
FLASK_SECRET_KEY=your-strong-random-secret-key
ADMIN_PASSWORD=your-admin-password

# ── Database (SQLite by default, no config needed) ────────
# For MySQL/PostgreSQL, update SQLALCHEMY_DATABASE_URI in app.py

# ── Email / OTP (optional) ────────────────────────────────
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password     # Gmail App Password

# ── AI Chatbot (optional) ─────────────────────────────────
OPENROUTER_API_KEY=your-openrouter-api-key
```

> ⚠️ The app will **refuse to start** if `FLASK_SECRET_KEY` or `ADMIN_PASSWORD` are missing.

---

## 📡 API Overview

All API endpoints are under `/api/` and return JSON. They are protected by session authentication.

### University & Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/university` | Get university configuration |
| PUT | `/api/university` | Update university settings |

### Departments, Courses, Faculty, Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/departments` | List / create departments |
| GET/PUT/DELETE | `/api/departments/<id>` | Read / update / delete |
| GET/POST | `/api/courses` | List / create courses |
| GET/POST | `/api/faculty` | List / create faculty |
| GET/POST | `/api/students` | List / create students |

### Timetable
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/timetable/generate` | Generate full timetable |
| POST | `/api/timetable/generate/<dept_id>` | Partial regeneration |
| GET | `/api/timetable/section/<id>` | Section timetable |
| GET | `/api/timetable/faculty/<id>` | Faculty timetable |
| GET | `/api/timetable/student` | Current student's timetable |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/attendance/session/start` | Faculty starts QR session |
| GET | `/api/attendance/session/qr/<token>` | Get rolling QR token |
| GET | `/api/attendance/session/live/<token>` | Live attendance list |
| POST | `/api/attendance/session/stop` | Stop session & commit records |
| POST | `/api/attendance/submit` | Student submits attendance |
| POST | `/api/attendance/manual-save` | Manual faculty override |

### Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/student` | Student AI chat |
| POST | `/api/chatbot/faculty` | Faculty AI chat |
| POST | `/api/chatbot/admin` | Admin AI chat |

---

## ☁️ Deployment (Render)

This project is deployed on **Render** as a web service.

### Deploy Steps
1. Push code to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repository
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:** Add all variables from `.env`

> 💡 Add `gunicorn` to `requirements.txt` for Render deployment.

---

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@srmap.edu.in` | Set via `ADMIN_PASSWORD` in `.env` |
| Faculty | `firstname.lastname@srmap.edu.in` | `firstname@123` |
| Student | `firstname.lastname@srmap.edu.in` | `firstname@123` |

> All emails must end with `@srmap.edu.in` to be accepted by the login system.

---

## 📸 Screenshots

| Admin Dashboard | Faculty Dashboard | Student Dashboard |
|:-:|:-:|:-:|
| Manage university, departments, courses, rooms | Personal timetable, attendance sessions, AI chat | Weekly schedule, attendance tracker, QR scanner |

---

## 👥 Contributors

| Name | Role |
|------|------|
| Harshavardhan | Project Lead & Developer |

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

Made with ❤️ for SRM AP University

⭐ Star this repo if you found it useful!

</div>
