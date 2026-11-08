# Backend

A Python backend project built with **FastAPI, PostgreSQL 16, and Docker Compose**. This project demonstrates REST API development, request and response validation, dependency injection, relational database fundamentals, automated testing, and continuous integration.

## Technology Stack

- Python 3.12
- FastAPI and Pydantic
- PostgreSQL 16
- Docker and Docker Compose
- Pytest
- Ruff
- GitHub Actions
- DBeaver Community

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
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Features

- REST API development using FastAPI.
- Pydantic request and response models.
- Email validation using `EmailStr`.
- Path and query parameter handling.
- Dependency injection using `Depends`.
- HTTP exception handling for missing student records.
- PostgreSQL 16 service configured through Docker Compose.
- Automated tests using Pytest.
- Code quality checks using Ruff.
- Separate linting and testing jobs in GitHub Actions.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a welcome message |
| GET | `/health` | Returns API health status |
| POST | `/students` | Creates a student record |
| GET | `/students/{student_id}` | Retrieves a student by ID |
| GET | `/students` | Lists students with optional filtering and pagination |

### Example: Create a Student

**Request**

```json
{
  "name": "Ali",
  "email": "ali@example.com",
  "age": 20,
  "department": "CS"
}
```

**Response**

```json
{
  "student_id": 3,
  "name": "Ali",
  "email": "ali@example.com",
  "age": 20,
  "department": "CS"
}
```

### Example: Retrieve a Student

```http
GET /students/1
```

### Example: Filter Students

```http
GET /students?department=CS&limit=5
```

The `limit` parameter accepts values from 1 to 100 and defaults to 10.

**Note:** Student records are currently stored in an in-memory Python dictionary. They are not persisted in PostgreSQL and are reset when the application restarts.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/AMAN-AJWA-FATIMA/Backend.git
cd Backend
```

### 2. Create and activate a virtual environment

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

Access the application:

- API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Interactive documentation: http://127.0.0.1:8000/docs

## Docker Setup

### 1. Configure environment variables

Create a local `.env` file using the example:

```bash
cp .env.example .env
```

Set the PostgreSQL username, password, and database name in `.env`.

Do not commit `.env` or expose real database credentials.

### 2. Build and start services

```bash
docker compose up -d --build
```

### 3. Check service status

```bash
docker compose ps
```

The Compose configuration starts:

- **API:** FastAPI application on port `8000`.
- **Database:** PostgreSQL 16 on host port `5433`, mapped to container port `5432`.

The database has a health check, and the API service waits for the database health check before starting.

### 4. Stop services

```bash
docker compose down
```

To also remove the database volume and its stored data:

```bash
docker compose down -v
```

Use the volume-removal command carefully because it deletes the database's persisted data.

## PostgreSQL Practical

PostgreSQL was configured as a separate Docker service and explored using DBeaver.

The practical exercises covered:

- Creating relational tables: `departments` and `students`.
- Defining primary keys and foreign keys.
- Applying `NOT NULL`, `UNIQUE`, and `CHECK` constraints.
- Inserting sample records.
- Retrieving related data using `INNER JOIN`.
- Creating and inspecting indexes.

### Example JOIN Query

```sql
SELECT
    s.student_id,
    s.name,
    s.email,
    d.department_name
FROM students s
INNER JOIN departments d
    ON s.department_id = d.department_id;
```

### Indexes Verified

- `students_pkey` — primary key index.
- `students_email_key` — unique email index.
- `idx_students_department_id` —
