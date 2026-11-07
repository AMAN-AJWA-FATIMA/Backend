
# Backend

A backend application developed using FastAPI and PostgreSQL as part of the backend setup task.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- Pytest
- Ruff
- Docker and Docker Compose

## Project Structure

```text
backend/
├── app/
│   └── main.py
├── tests/
│   └── test_healthy.py
├── .gitignore
├── README.md
└── pyproject.toml
```

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install "fastapi[standard]" pytest ruff
```

### 4. Run the application

```bash
fastapi dev app/main.py
```

Open:
- Health check: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

## Testing

Run automated tests:

```bash
python -m pytest -v
```

## Code Quality

Run Ruff:

```bash
ruff check .
```
