live server : https://no-nk4fn9r0g-deepu-gs-projects.vercel.app
# No-Due Clearance Management System

A full-stack web application that digitizes the college no-due clearance process with a multi-level approval workflow.

**Workflow:** Student → Faculty Approval → Admin/Department Clearance → HOD Approval → Hall Ticket Issued

## Tech Stack
- **Frontend:** React 18 + Vite + Tailwind CSS 3
- **Backend:** Python Flask + Flask-JWT-Extended
- **Database:** PostgreSQL

---

## Quick Setup

### Prerequisites
- [Python 3.9+](https://python.org)
- [Node.js 18+](https://nodejs.org)
- [PostgreSQL 14+](https://postgresql.org)

### 1. Database Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE nodue_db;"

# Run schema
psql -U postgres -d nodue_db -f backend/schema.sql

# Load sample data
psql -U postgres -d nodue_db -f backend/seed_data.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure (edit config.py or set env vars)
# DB_USER=postgres DB_PASSWORD=postgres DB_NAME=nodue_db

# Run server
python app.py
# → Running on http://localhost:5000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API to :5000)
npm run dev
# → Running on http://localhost:5173
```

## Project Structure

```
no_due/
├── backend/
│   ├── app.py              # Flask entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Python deps
│   ├── schema.sql           # Database DDL
│   ├── seed_data.sql        # Sample data
│   ├── models/              # Database models
│   │   ├── __init__.py      # DB connection helper
│   │   ├── user.py
│   │   ├── request.py
│   │   ├── approval.py
│   │   ├── notification.py
│   │   └── department.py
│   └── routes/              # API endpoints
│       ├── auth.py
│       ├── student.py
│       ├── faculty.py
│       ├── admin.py
│       ├── hod.py
│       ├── staff.py
│       ├── notifications.py
│       └── analytics.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/axios.js
│       ├── context/AuthContext.jsx
│       ├── components/
│       │   ├── Layout.jsx
│       │   └── StatusTracker.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Signup.jsx
│           ├── student/Dashboard.jsx
│           ├── faculty/Dashboard.jsx
│           ├── admin/Dashboard.jsx
│           ├── hod/Dashboard.jsx
│           └── staff/Dashboard.jsx
└── README.md
