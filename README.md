# Secure User Authentication: React + Django REST Framework

A minimal, interview-ready example of **token-based authentication** with **HttpOnly cookies**, **refresh token rotation**, and **CSRF protection** across a React frontend and Django REST Framework backend.

## Quick start

**Backend (Django)** (Python 3.7+)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # create a user to log in with
python manage.py runserver
```

**Frontend (React)**

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173 (proxies `/api` to the backend)
- Backend: http://127.0.0.1:8000

Log in with your superuser (or create a normal user via Django admin at http://127.0.0.1:8000/admin/).
