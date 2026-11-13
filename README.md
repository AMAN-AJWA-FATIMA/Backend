# Backend — # API Skeleton with Secure Login and Roles

A containerized backend application built with **Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2, and Docker Compose**.

The project demonstrates REST API development, relational database integration, request validation, authentication, role-based authorization, database migrations, automated testing, and continuous integration.

It includes a task-management API and an authentication system with secure password hashing, short-lived access tokens, rotating refresh tokens, and role-protected endpoints.

## 1. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend programming language |
| FastAPI | REST API framework |
| Pydantic | Request validation and response schemas |
| SQLAlchemy 2 | ORM and database operations |
| PostgreSQL 16 | Relational database |
| Alembic | Database schema migrations |
| Argon2id | Password hashing |
| PyJWT | JWT access-token generation and validation |
| Docker & Docker Compose | Containerization and service orchestration |
| Pytest | Automated testing |
| HTTPX | API testing |
| Ruff | Linting and code quality |
| Git & GitHub | Version control |
| GitHub Actions | Continuous integration |
| DBeaver | Database administration and inspection |

## 2. Project Structure

```text
Backend/
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── versions/
│   │   └── 20261113_01_authentication.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── dependencies/
│   │   ├── authentication.py
│   │   └── permissions.py
│   ├── models/
│   │   ├── refresh_token.py
│   │   └── user.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── authorization_demo.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── task.py
│   │   └── user.py
│   └── main.py
├── scripts/
│   └── create_admin.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_healthy.py
│   ├── test_tasks.py
│   └── test_users.py
├── web/
│   └── index.html
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 3. Core Features

### Task Management API

The existing API provides operations for managing users and tasks.

Implemented capabilities include:

- Creating and retrieving user records.
- Listing users with pagination.
- Validating email addresses.
- Creating, retrieving, updating, and deleting tasks.
- Handling nonexistent records and invalid requests.
- Filtering and paginating task results.
- Managing database relationships and constraints.

The task and user endpoints use the application's existing database implementation.

### Authentication

The authentication module provides:

- User registration.
- Login with email and password.
- JWT access-token issuance.
- Refresh-token rotation.
- Refresh-token revocation on logout.
- Authenticated user profile retrieval.
- Protected endpoints using HTTP Bearer authentication.

### Role-Based Authorization

The application supports three roles:

| Role | Description |
|---|---|
| `student` | Standard student account |
| `parent` | Parent account |
| `admin` | Administrative account |

A reusable `require_roles()` dependency enforces endpoint permissions.

Example authorization rules:

| Endpoint | Allowed roles |
|---|---|
| `GET /admin/dashboard` | admin |
| `GET /parent/dashboard` | parent, admin |
| `GET /auth/me` | Any authenticated user |

Public registration permits only `student` and `parent` roles. Administrative accounts must be provisioned separately.

## 4. Authentication Architecture

### Password Security

Passwords are hashed using **Argon2id** through `argon2-cffi`.

- Plaintext passwords are never stored in the database.
- Password verification uses the stored Argon2 hash.
- Invalid credentials return HTTP 401.
- Public registration validates password length.
- Administrative account creation uses interactive password entry.

### Access Tokens

Access tokens are signed JWTs using HS256.

| Property | Configuration |
|---|---|
| Token type | JWT |
| Signing algorithm | HS256 |
| Lifetime | 15 minutes |
| Authentication scheme | Bearer |
| Required claims | `sub`, `iat`, `exp`, `type` |
| Token identifier | `jti` |

Protected endpoints validate the token signature, expiration, token type, and associated user.

### Refresh Tokens

Refresh tokens are opaque, cryptographically random values.

| Property | Configuration |
|---|---|
| Token lifetime | 14 days |
| Generation | Python `secrets` |
| Database storage | SHA-256 digest |
| Rotation | Enabled |
| Revocation | Supported |
| User relationship | Foreign key to `users` |

The application stores only the SHA-256 digest of each refresh token, not its original value.

When a refresh token is used:

1. The submitted token is hashed.
2. Its corresponding database record is retrieved.
3. The application checks whether it exists, has expired, or has been revoked.
4. The old token is revoked.
5. A new access token and refresh token are issued.
6. The new refresh-token digest is stored.

Logout revokes the submitted refresh token. A revoked or previously rotated refresh token cannot be used again.

### Authentication Flow

```text
Registration
    |
    v
User account created
    |
    v
Login with email and password
    |
    v
Password verification (Argon2id)
    |
    v
Access token + Refresh token
    |
    +--------------------------+
    |                          |
    v                          v
Access protected API       Refresh access
    |                          |
    v                          v
Validate JWT              Validate refresh token
    |                          |
    v                          v
Authorize user            Revoke old token
    |                          |
    v                          v
Return response           Issue new token pair
                               |
                               v
                         Continue session

Logout
    |
    v
Revoke refresh token
    |
    v
Further refresh attempts rejected
```

**Note:** Revoking a refresh token prevents future token renewal. An already issued access JWT remains valid until its expiration because access-token revocation through a denylist is not currently implemented.

## 5. API Reference

The following endpoints are implemented by the application.

### General Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the web interface |
| GET | `/health` | Application health check |

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/auth/register` | Register a student or parent | Public |
| POST | `/auth/login` | Authenticate and issue tokens | Public |
| POST | `/auth/refresh` | Rotate refresh token and issue new tokens | Refresh token |
| POST | `/auth/logout` | Revoke refresh token | Refresh token |
| GET | `/auth/me` | Retrieve authenticated user profile | Bearer token |

### Authorization Demonstration Endpoints

| Method | Endpoint | Allowed roles |
|---|---|---|
| GET | `/admin/dashboard` | admin |
| GET | `/parent/dashboard` | parent, admin |

### User and Task Endpoints

The application also exposes the existing user and task-management routes:

- `/users`
- `/users/{user_id}`
- `/tasks`
- `/tasks/{task_id}`

Consult Swagger UI for the exact request schemas, supported methods, query parameters, and response models.

## 6. Request Examples

### Register a User

**POST `/auth/register`**

```json
{
  "full_name": "Ali Ahmed",
  "email": "ali@example.com",
  "password": "StrongPassword123!",
  "role": "student"
}
```

A successful registration returns HTTP 201 and the created user profile.

The public registration schema accepts `student` and `parent` roles only.

### Login

**POST `/auth/login`**

```json
{
  "email": "ali@example.com",
  "password": "StrongPassword123!"
}
```

A successful login returns HTTP 200.

Example response structure:

```json
{
  "access_token": "<access-token>",
  "token_type": "bearer",
  "expires_in": 900,
  "refresh_token": "<refresh-token>",
  "refresh_expires_in": 1209600
}
```

The example values represent the configured token lifetimes. Actual token values are generated dynamically.

### Access the Current User

**GET `/auth/me`**

Include the access token in the request header:

```http
Authorization: Bearer <access-token>
```

Returns the authenticated user's profile.

### Refresh Tokens

**POST `/auth/refresh`**

```json
{
  "refresh_token": "<refresh-token>"
}
```

Returns a new access token and refresh token. The previous refresh token is revoked.

### Logout

**POST `/auth/logout`**

```json
{
  "refresh_token": "<refresh-token>"
}
```

A successful logout returns HTTP 204 No Content.

Subsequent attempts to refresh using the revoked token return HTTP 401.

### Authorization

**GET `/admin/dashboard`**

A valid student access token receives HTTP 403 Forbidden.

An authenticated admin receives access.

**GET `/parent/dashboard`**

Parent and admin accounts are permitted to access this endpoint.

## 7. Database Design

The application uses PostgreSQL 16 and SQLAlchemy 2.

The authentication implementation extends the existing `users` table and introduces a separate `refresh_tokens` table.

### Users Table

Authentication-related fields:

| Column | Purpose |
|---|---|
| `id` | Primary key |
| `full_name` | User's full name |
| `email` | User email address |
| `password_hash` | Argon2id password hash |
| `role` | User authorization role |
| `created_at` | Account creation timestamp |

The existing user fields and relationships are retained.

`password_hash` is nullable to preserve legacy user records created before authentication was introduced. Those accounts cannot authenticate until credentials are provisioned.

### Refresh Tokens Table

| Column | Purpose |
|---|---|
| `id` | Primary key |
| `user_id` | Foreign key referencing users |
| `token_hash` | SHA-256 digest of refresh token |
| `expires_at` | Token expiration timestamp |
| `revoked_at` | Revocation timestamp; nullable |
| `created_at` | Token creation timestamp |

Database constraints and indexes include:

- Primary key on `id`.
- Foreign key from `user_id` to `users.id`.
- Unique constraint on `token_hash`.
- Index on `user_id`.

## 8. Database Migrations with Alembic

Alembic manages database schema changes.

The authentication migration:

`alembic/versions/20261113_01_authentication.py`

It performs the following operations:

1. Adds `password_hash` to the existing users table.
2. Adds a `role` column with a default of `student`.
3. Creates the `refresh_tokens` table.
4. Adds the required foreign key and unique constraint.
5. Creates an index on `refresh_tokens.user_id`.

The migration preserves existing user records and does not require recreating the database.

### Apply Migrations

```bash
alembic upgrade head
```

### Check Migration Status

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

The Docker API container automatically applies migrations before starting the application.

## 9. Environment Configuration and Secrets

Sensitive configuration is provided through environment variables.

Create a local `.env` file in the repository root using `.env.example` as a template.

```bash
cp .env.example .env
```

Edit the local file:

```bash
nano .env
```

Configure the following variables with appropriate local values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=replace_with_a_strong_local_password
POSTGRES_DB=task_management_db

DB_HOST=localhost
DB_PORT=5433
DB_NAME=task_management_db
DB_USER=task_management_app
DB_PASSWORD=replace_with_a_strong_local_password

JWT_SECRET_KEY=replace_with_a_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=14
```

The API container connects to PostgreSQL using the Docker service hostname `db` and container port `5432`. The `DB_HOST` and `DB_PORT` values above are for local execution outside Docker.

## 10. Running the Project with Docker Compose

### Prerequisites

- Python 3.12
- Git
- Docker Engine
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/AMAN-AJWA-FATIMA/Backend.git
cd Backend
```

### Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Replace placeholder values with valid local credentials. Use the same PostgreSQL password for `POSTGRES_PASSWORD` and `DB_PASSWORD` when using the provided initialization configuration.

### Start the Application

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up -d --build
```

Docker Compose starts:

| Service | Container | Port |
|---|---|---|
| FastAPI | `backend_api` | `8000` |
| PostgreSQL | `backend_db` | `5433` on host, `5432` in container |

The API service waits for the database health check before starting. It applies Alembic migrations and then launches Uvicorn.

### Verify Containers

```bash
docker compose ps
```

### Check API Health

```bash
curl -i http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Open the Application

- Web interface: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health endpoint: http://localhost:8000/health

### Stop the Application

```bash
docker compose down
```

This stops and removes the containers while retaining the named PostgreSQL volume.

**Important:** Avoid `docker compose down -v` unless you intentionally want to delete the PostgreSQL volume and all database data stored in it.

## 11. Running Locally Without Docker

Docker Compose is the recommended way to run the complete application.

For local Python development, first ensure PostgreSQL is available and the environment variables are configured for the local database connection.

### Create a Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Apply Database Migrations

```bash
alembic upgrade head
```

### Start FastAPI

```bash
uvicorn app.main:app --reload
```

The application will be available at:

`http://127.0.0.1:8000`

## 12. Administrator Account Provisioning

Administrator accounts cannot be created through public registration.

Use the dedicated CLI script:

```bash
python -m scripts.create_admin
```

The script:

1. Requests the administrator's full name.
2. Requests an email address.
3. Prompts for a password without displaying it.
4. Requires password confirmation.
5. Enforces a minimum password length of 12 characters.
6. Hashes the password using Argon2id.
7. Creates an account with the `admin` role.

Ensure database connectivity and migrations are ready before running the command.

## 13. Web Interface

A simple web interface is provided in `web/index.html`.

It demonstrates:

- User registration.
- User login.
- Accessing the authenticated profile.
- Refreshing access tokens.
- Logging out.
- Testing role-protected endpoints.

Tokens are held in page memory rather than browser local storage or session storage. Reloading the page requires logging in again.

The interface is intended as an integration demonstration, not a production-ready frontend.

## 14. Testing

The project uses Pytest and HTTPX to validate API behavior.

Run the complete test suite:

```bash
pytest -v
```

### Authentication Test Coverage

The authentication tests verify:

| Test | Expected result |
|---|---|
| User registration and login | Successful registration and authentication |
| Incorrect password | HTTP 401 |
| Authenticated profile | HTTP 200 |
| Expired access token | HTTP 401 |
| Refresh-token rotation | New token issued |
| Reuse of rotated token | HTTP 401 |
| Logout revocation | HTTP 204 |
| Reuse of revoked token | HTTP 401 |
| Student accessing admin endpoint | HTTP 403 |
| Parent accessing parent endpoint | HTTP 200 |
| Public admin registration attempt | HTTP 422 |

The existing health, user, and task tests are also retained.

### Latest Local Test Results

The latest verified local run reported:

- **26 tests passed**
- No test failures.
- Ruff linting passed.

These results describe the local test run; the GitHub Actions result should be checked separately after pushing the changes.

## 15. Code Quality

Ruff is used for linting and import checks.

Run:

```bash
ruff check .
```

Format the project:

```bash
ruff format .
```

Validate Docker Compose configuration:

```bash
docker compose config -q
```

Check the current migration:

```bash
docker compose exec api alembic current
```

## 16. Continuous Integration

GitHub Actions runs automated checks for pushes to `main` and pull requests targeting `main`.

Workflow location:

`.github/workflows/ci.yml`

The pipeline uses Python 3.12 and contains two jobs:

### Ruff Linting

- Checks out the repository.
- Sets up Python 3.12.
- Installs dependencies.
- Runs `ruff check .`.

### Pytest

- Checks out the repository.
- Sets up Python 3.12.
- Installs dependencies.
- Runs `pytest -v`.

Workflow execution results are available under the repository's **Actions** tab.

## 17. Known Limitations

- Existing legacy user accounts have nullable `password_hash` values. They require a separate credential-enrollment or password-reset process before they can authenticate.
- Access JWTs are not invalidated immediately on logout; they remain valid until expiration. Refresh-token revocation prevents renewal.
- The web interface is a basic demonstration and is not intended for production deployment.
- The API does not currently implement email verification, password-reset workflows, or rate limiting.
- The local CI workflow runs linting and automated tests; it does not currently build and run the Docker services.

## 18. Repository and Documentation

**GitHub Repository:**  
https://github.com/AMAN-AJWA-FATIMA/Backend

**API Documentation:**  
http://localhost:8000/docs

**Alternative API Documentation:**  
http://localhost:8000/redoc

The documentation endpoints are available when the application is running.

---
