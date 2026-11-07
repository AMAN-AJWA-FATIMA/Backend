
# Backend

A Python backend application built with FastAPI, PostgreSQL, and Docker Compose. This project demonstrates REST API development, request validation, automated testing, code quality checks, and containerized services.

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic
- PostgreSQL 16
- Docker and Docker Compose
- Pytest
- Ruff
- GitHub Actions

## Project Structure

```text
Backend/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_healthy.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Features

- FastAPI application with automatic API documentation.
- Health-check endpoint for service monitoring.
- Student creation endpoint using Pydantic request validation.
- PostgreSQL 16 service configured through Docker Compose.
- Automated testing with Pytest.
- Code quality checks using Ruff.
- Separate linting and testing jobs in GitHub Actions.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | API health status |
| POST | `/students` | Accept student information |

### Example: Create a Student

Request:

```json
{
  "name": "Aman",
  "email": "aman@example.com",
  "age": 20
}
```

Response:

```json
{
  "message": "Student created successfully",
  "student": {
    "name": "Aman",
    "email": "aman@example.com",
    "age": 20
  }
}
```

The current student endpoint validates and returns the submitted data. Persistent database storage has not yet been integrated.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/AMAN-AJWA-FATIMA/Backend.git
cd Backend
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the API

```bash
fastapi dev app/main.py
```

Open the following URLs:

- API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

## Docker Setup

Build and start the application and database:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

Stop the services:

```bash
docker compose down
```

The API is available at port `8000`. PostgreSQL is exposed on host port `5433` and uses port `5432` inside the container.

## Testing

Run the automated tests:

```bash
python -m pytest -v
```

## Code Quality

Run Ruff:

```bash
ruff check .
```

## Continuous Integration

GitHub Actions runs two independent jobs on pushes and pull requests targeting `main`:

- **Ruff Linting:** checks code quality and formatting-related lint rules.
- **Pytest:** executes the automated test suite.

Workflow configuration: `.github/workflows/ci.yml`.

## Database

PostgreSQL 16 is configured as a separate service in Docker Compose. The database service has a health check and persistent Docker volume.

The API currently runs independently of database persistence. Database integration and SQL practice examples can be added as a subsequent development step.

## Repository

https://github.com/AMAN-AJWA-FATIMA/Backend
