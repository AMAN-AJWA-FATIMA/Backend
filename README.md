# Backend

A Python backend project developed using **FastAPI, PostgreSQL 16, and Docker Compose**. It demonstrates the fundamentals of backend development, including REST API design, request validation, dependency injection, relational database operations, containerization, automated testing, and continuous integration using GitHub Actions.

The project focuses on building a structured, maintainable backend environment while gaining practical experience with modern backend development tools and workflows.

## 1. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend programming |
| FastAPI | REST API development |
| Pydantic | Request validation and response models |
| PostgreSQL 16 | Relational database |
| Docker & Docker Compose | Containerization and service orchestration |
| DBeaver | PostgreSQL database management |
| Pytest | Automated testing |
| Ruff | Linting and code quality |
| Git & GitHub | Version control and collaboration |
| GitHub Actions | Continuous integration |

## 2. Project Structure

```text
Backend/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   └── main.py
├── tests/
│   └── test_healthy.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 3. Implemented Features

- FastAPI application with automatic interactive API documentation.
- Health-check endpoint.
- REST endpoints for student records.
- Pydantic request validation using `BaseModel` and `EmailStr`.
- Response models for structured API responses.
- Path parameters and query parameters.
- Dependency injection using `Depends`.
- Query validation and pagination limits.
- HTTP exception handling, including 404 responses.
- PostgreSQL 16 container configured with persistent storage.
- Automated testing with Pytest.
- Code quality checks with Ruff.
- GitHub Actions workflow for continuous integration.

## 4. API Endpoints

The application exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a welcome message |
| GET | `/health` | Checks application health |
| POST | `/students` | Creates a student record |
| GET | `/students/{student_id}` | Retrieves a student by ID |
| GET | `/students` | Lists students with optional filtering and pagination |

### Request and Response Example

**POST `/students`**

Request body:

```json
{
  "name": "Ali",
  "email": "ali@example.com",
  "age": 20,
  "department": "CS"
}
```

Example response:

```json
{
  "name": "Ali",
  "email": "ali@example.com",
  "age": 20,
  "department": "CS",
  "student_id": 4
}
```

### Path Parameter

**GET `/students/1`**

Retrieves the student whose ID is `1`. Returns HTTP 404 if the student does not exist.

### Query Parameters

**GET `/students?department=CS&limit=5`**

- `department`: Optional department filter.
- `limit`: Maximum number of returned records.
- Default limit: `10`.
- Accepted limit range: `1–100`.

### Interactive API Documentation

FastAPI automatically generates API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 5. Application Data Storage

The student endpoints currently use an in-memory Python dictionary for demonstration purposes.

This implementation demonstrates REST API operations, request validation, response models, and dependency injection. Student records are not currently persisted to PostgreSQL, and in-memory records reset when the application restarts.

PostgreSQL is configured separately and was used for the database practical exercises documented below.

## 6. Local Development Setup

### Prerequisites

- Python 3.12
- Git
- PostgreSQL client
- Docker and Docker Compose

### Clone the Repository

```bash
git clone https://github.com/AMAN-AJWA-FATIMA/Backend.git
cd Backend
```

### Create and Activate Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
fastapi dev app/main.py
```

The application will be available at:

`http://127.0.0.1:8000`

## 7. Docker Setup

The project uses Docker Compose to run the FastAPI application and PostgreSQL 16 as separate services.

### Environment Configuration

Create a local `.env` file using the example configuration:

```bash
cp .env.example .env
```

Update the values in `.env` with your local database credentials.

The `.env` file is excluded from version control. Do not commit actual credentials.

### Start the Services

```bash
docker compose up --build
```

Run the services in detached mode:

```bash
docker compose up -d --build
```

### Verify Running Containers

```bash
docker compose ps
```

The API service is exposed on port `8000`. PostgreSQL is exposed on host port `5433` and uses container port `5432`.

### Check Application Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Stop the Services

```bash
docker compose down
```

To remove the PostgreSQL volume and its stored data as well:

```bash
docker compose down -v
```

**Warning:** The `-v` option deletes the database volume and its contents.

## 8. PostgreSQL Practical

PostgreSQL 16 was configured through Docker Compose and accessed using DBeaver.

The database exercises covered relational database fundamentals, including table creation, primary keys, foreign keys, constraints, joins, and indexes.

### Database Tables

Two related tables were created:

**departments**

| Column | Description |
|---|---|
| `department_id` | Primary key |
| `department_name` | Department name |

**students**

| Column | Description |
|---|---|
| `student_id` | Primary key |
| `name` | Student name |
| `email` | Unique student email |
| `department_id` | Foreign key referencing departments |

### Database Operations Practised

- `CREATE TABLE` — creating relational tables.
- Primary keys — uniquely identifying records.
- Foreign keys — establishing relationships between tables.
- `INSERT` — adding records.
- `SELECT` — retrieving records.
- `INNER JOIN` — retrieving related student and department information.
- `CREATE INDEX` — improving lookup performance.

### JOIN Query

```sql
SELECT
    s.name,
    s.email,
    d.department_name
FROM students AS s
INNER JOIN departments AS d
    ON s.department_id = d.department_id;
```

The query successfully retrieved student names, email addresses, and their associated department names.

### Indexes Verified

| Index | Purpose |
|---|---|
| `students_pkey` | Primary key index on `student_id` |
| `students_email_key` | Unique index on `email` |
| `idx_students_department_id` | Index on `department_id` |

## 9. Testing and Code Quality

### Automated Tests

Pytest is used to verify application behavior.

Run the test suite:

```bash
pytest -v
```

The health-check test verifies that:

- The `/health` endpoint responds successfully.
- The returned status is HTTP 200.
- The response contains `{"status": "healthy"}`.

### Code Quality

Ruff is used for linting and import checks.

```bash
ruff check .
```

### Configuration Validation

Docker Compose configuration can be validated using:

```bash
docker compose config -q
```

## 10. Continuous Integration

GitHub Actions is configured to run automated checks when code is pushed to the `main` branch or a pull request targets it.

The workflow is located at:

`.github/workflows/ci.yml`

The CI pipeline uses Python 3.12 and installs the project dependencies before running:

1. **Ruff Linting** — checks the code for linting and import issues.
2. **Pytest** — executes the automated test suite.

Workflow results can be viewed under the repository's **Actions** tab.

## 11. Learning Outcomes

This project provided practical experience with:

- Setting up a Python backend development environment.
- Building REST APIs using FastAPI.
- Working with Pydantic models and request validation.
- Understanding path parameters, query parameters, and dependency injection.
- Creating relational database tables and defining relationships.
- Performing SQL queries, joins, and index verification.
- Running services through Docker Compose.
- Writing automated tests with Pytest.
- Applying linting standards with Ruff.
- Configuring a GitHub Actions CI workflow.
- Managing project changes through Git and GitHub.

## 12. Repository

**GitHub Repository:** [AMAN-AJWA-FATIMA/Backend](https://github.com/AMAN-AJWA-FATIMA/Backend)

**API Documentation:** `http://localhost:8000/docs` (available when the application is running).

---

