# Local Development & Testing Guide

## Local Prerequisites

- Python 3.12+
- Node.js 18+ / npm
- Docker (optional)

---

## 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -e ".[dev]"
```

Run tests:
```bash
pytest -v
```

Start dev server:
```bash
uvicorn app.main:app --reload --port 8000
```

---

## 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in browser.
