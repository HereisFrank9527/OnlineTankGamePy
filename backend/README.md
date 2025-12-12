# Backend - FastAPI Service

A modern, async FastAPI backend service with PostgreSQL, Redis, and JWT authentication.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL support via asyncpg
- **Redis** - For caching and real-time features
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **Pydantic Settings** - Type-safe configuration management
- **Poetry** - Dependency management and packaging
- **Pytest** - Comprehensive testing setup with async support

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory and lifespan management
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── rooms.py         # Room management endpoints
│   │   └── gameplay.py      # Gameplay endpoints
│   ├── services/            # Business logic layer
│   ├── schemas/             # Pydantic models for request/response
│   └── core/                # Core functionality
│       ├── config.py        # Configuration using Pydantic Settings
│       ├── database.py      # Database connection and session management
│       ├── redis.py         # Redis connection management
│       ├── security.py      # JWT and password hashing utilities
│       └── logging.py       # Logging configuration
├── tests/                   # Test suite
│   └── conftest.py          # Pytest fixtures and configuration
├── pyproject.toml           # Poetry dependencies and project metadata
├── .env.example             # Example environment variables
└── README.md                # This file
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Poetry (recommended) or pip

## Environment Setup

### 1. Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install Dependencies

```bash
cd backend
poetry install
```

Or with pip:

```bash
cd backend
pip install -e .
```

### 3. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and set the required variables:

**Required Variables:**

- `DATABASE_URL` - PostgreSQL connection string
  - Format: `postgresql+asyncpg://user:password@host:port/dbname`
  - Example: `postgresql+asyncpg://postgres:postgres@localhost:5432/myapp`

- `REDIS_URL` - Redis connection string
  - Format: `redis://host:port/db`
  - Example: `redis://localhost:6379/0`

- `SECRET_KEY` - JWT signing key (MUST be changed in production)
  - Generate with: `openssl rand -hex 32`

**Optional Variables:**

- `DEBUG` - Enable debug mode (default: `false`)
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: `INFO`)
- `PORT` - Server port (default: `8000`)
- `RELOAD` - Enable auto-reload on code changes (default: `false`)
- `DB_ECHO` - Echo SQL queries (default: `false`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT access token expiration (default: `30`)
- `REFRESH_TOKEN_EXPIRE_DAYS` - JWT refresh token expiration (default: `7`)
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins (default: `["http://localhost:3000","http://localhost:5173"]`)

### 4. Setup Database and Redis

Make sure PostgreSQL and Redis are running:

**PostgreSQL:**
```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  postgres:16
```

**Redis:**
```bash
# Using Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7
```

Or use local installations:
```bash
# PostgreSQL
sudo systemctl start postgresql

# Redis
sudo systemctl start redis
```

## Running the Server

### Development Mode (with hot reload)

Using Poetry:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or activate the virtual environment first:
```bash
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Using pip:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

With Gunicorn (recommended for production):
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## API Documentation

Once the server is running, visit:

- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI JSON schema:** http://localhost:8000/openapi.json

## Available Endpoints

### Health Check
- `GET /health` - Service health status

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `POST /logout` - User logout
- `GET /me` - Get current user info

#### Request/Response Examples

**Register**

`POST /api/v1/auth/register`

Request body:
```json
{
  "username": "tank_master",
  "email": "tank_master@example.com",
  "password": "password123"
}
```

Response (`201`):
```json
{
  "id": 1,
  "username": "tank_master",
  "email": "tank_master@example.com",
  "last_login_at": null,
  "login_count": 0,
  "kills": 0,
  "deaths": 0,
  "wins": 0,
  "losses": 0,
  "games_played": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Login**

`POST /api/v1/auth/login`

Request body:
```json
{
  "username": "tank_master",
  "password": "password123"
}
```

Response (`200`):
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

**Get Profile**

`GET /api/v1/auth/me`

Request header:
```
Authorization: Bearer <access_token>
```

### Rooms (`/api/v1/rooms`)
- `GET /` - List all rooms
- `POST /` - Create new room
- `GET /{room_id}` - Get room details
- `PUT /{room_id}` - Update room
- `DELETE /{room_id}` - Delete room
- `POST /{room_id}/join` - Join room
- `POST /{room_id}/leave` - Leave room

### Gameplay (`/api/v1/gameplay`)
- `GET /state/{room_id}` - Get game state
- `POST /action/{room_id}` - Perform game action
- `POST /start/{room_id}` - Start game
- `POST /end/{room_id}` - End game

## Testing

Run the test suite:

```bash
poetry run pytest
```

With coverage report:

```bash
poetry run pytest --cov=app --cov-report=html
```

Run specific tests:

```bash
poetry run pytest tests/test_auth.py -v
```

## Code Quality

### Formatting with Black

```bash
poetry run black app tests
```

### Linting with Ruff

```bash
poetry run ruff check app tests
```

Fix auto-fixable issues:

```bash
poetry run ruff check --fix app tests
```

## Database Migrations

This project uses Alembic for database migrations.

### Create a new migration

```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
poetry run alembic upgrade head
```

### Rollback migration

```bash
poetry run alembic downgrade -1
```

## Development Workflow

1. Create a new feature branch
2. Make your changes
3. Run tests: `poetry run pytest`
4. Format code: `poetry run black app tests`
5. Lint code: `poetry run ruff check app tests`
6. Commit and push changes
7. Create a pull request

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | FastAPI Backend | No |
| `APP_VERSION` | Application version | 0.1.0 | No |
| `DEBUG` | Debug mode | false | No |
| `API_V1_PREFIX` | API route prefix | /api/v1 | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `RELOAD` | Auto-reload on changes | false | No |
| `DATABASE_URL` | PostgreSQL connection URL | - | **Yes** |
| `DB_ECHO` | Echo SQL queries | false | No |
| `DB_POOL_SIZE` | Database pool size | 5 | No |
| `DB_MAX_OVERFLOW` | Max pool overflow | 10 | No |
| `REDIS_URL` | Redis connection URL | - | **Yes** |
| `REDIS_MAX_CONNECTIONS` | Max Redis connections | 10 | No |
| `SECRET_KEY` | JWT signing key | - | **Yes** |
| `ALGORITHM` | JWT algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | 30 | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 | No |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | [...] | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `LOG_FORMAT` | Log format | json | No |

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check credentials in `.env`
- Ensure database exists: `createdb myapp`

### Redis Connection Issues

- Verify Redis is running: `redis-cli ping`
- Check Redis URL in `.env`

### Import Errors

- Ensure you're in the backend directory
- Activate virtual environment: `poetry shell`
- Reinstall dependencies: `poetry install`

## License

[Your License Here]
