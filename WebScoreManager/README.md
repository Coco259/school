# WebScoreManager — Smoke Test and Setup

This folder contains a small Flask-based student/course/score manager. The `smoke_test.py` script performs an end-to-end smoke test (admin login, create course, create student, create score, student login, fetch scores, cleanup).

Prerequisites
- Python 3.10+ (venv recommended)
- MySQL server (or MariaDB)
- Dependencies listed in `requirements.txt` (Flask, PyMySQL)

Quick setup

1. Import the provided SQL schema to create a clean `school_db` with sample data:

```powershell
mysql -u root -p < "d:\桌面\School_db\WebScoreManager\setup_db.sql"
```

2. (Optional) Create and activate a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. Start the Flask app (from the `WebScoreManager` directory):

```powershell
python app.py
```

4. In another terminal, run the smoke test:

```powershell
python smoke_test.py
```

Notes
- The smoke test expects the default admin from `setup_db.sql` (username `admin`, password `admin123`). If you changed credentials, modify `smoke_test.py` accordingly.
- If your existing database schema differs, either import `setup_db.sql` or edit the top constants in `app.py` to match your schema.
