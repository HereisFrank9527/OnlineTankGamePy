# FastAPI Backend Project

A production-ready FastAPI backend service with PostgreSQL, Redis, and JWT authentication.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Option 1: Using Docker (Recommended for Development)

1. Start database and Redis:
   ```bash
   cd backend
   docker-compose up -d
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (SECRET_KEY is required!)
   ```

3. Run the server:
   ```bash
   ./run.sh
   # Or using make
   make run
   ```

### Option 2: Manual Setup

1. Install dependencies:
   ```bash
   cd backend
   
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Generate a secret key: openssl rand -hex 32
   # Update DATABASE_URL, REDIS_URL, and SECRET_KEY in .env
   ```

3. Start PostgreSQL and Redis (if not using Docker)

4. Run the development server:
   ```bash
   # With Poetry
   poetry run uvicorn app.main:app --reload
   
   # With pip
   uvicorn app.main:app --reload
   
   # Or using the provided script
   ./run.sh
   
   # Or using Make
   make run
   ```

### Access the Application

- **API**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Documentation

For detailed documentation, see [backend/README.md](backend/README.md)

## Development Commands

```bash
# Using Make (recommended)
make help          # Show all available commands
make install       # Install dependencies
make run           # Run development server
make test          # Run tests
make lint          # Run linter
make format        # Format code
make docker-up     # Start PostgreSQL and Redis
make docker-down   # Stop containers

# Database migrations
make migrate-create msg="description"  # Create migration
make migrate-up                        # Apply migrations
make migrate-down                      # Rollback migration
```

## Project Structure

```
.
├── backend/
│   ├── app/                    # Application code
│   │   ├── main.py            # FastAPI app factory
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── services/          # Business logic
│   │   └── schemas/           # Pydantic models
│   ├── tests/                 # Test suite
│   ├── alembic/               # Database migrations
│   ├── .env.example           # Environment template
│   ├── pyproject.toml         # Poetry dependencies
│   ├── requirements.txt       # Pip dependencies
│   ├── docker-compose.yml     # Local development stack
│   └── README.md              # Detailed documentation
└── README.md                  # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Rooms
- `GET /api/v1/rooms` - List rooms
- `POST /api/v1/rooms` - Create room
- `GET /api/v1/rooms/{room_id}` - Get room
- `PUT /api/v1/rooms/{room_id}` - Update room
- `DELETE /api/v1/rooms/{room_id}` - Delete room
- `POST /api/v1/rooms/{room_id}/join` - Join room
- `POST /api/v1/rooms/{room_id}/leave` - Leave room

### Gameplay
- `GET /api/v1/gameplay/state/{room_id}` - Get game state
- `POST /api/v1/gameplay/action/{room_id}` - Perform action
- `POST /api/v1/gameplay/start/{room_id}` - Start game
- `POST /api/v1/gameplay/end/{room_id}` - End game

## Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_main.py -v
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]
