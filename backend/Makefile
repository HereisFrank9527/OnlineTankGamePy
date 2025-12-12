.PHONY: help install run test lint format clean migrate-create migrate-up migrate-down docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make run            - Run development server with hot reload"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make lint           - Run linter (ruff)"
	@echo "  make format         - Format code with black"
	@echo "  make clean          - Remove cache and build files"
	@echo "  make migrate-create - Create new migration (usage: make migrate-create msg='description')"
	@echo "  make migrate-up     - Apply migrations"
	@echo "  make migrate-down   - Rollback last migration"
	@echo "  make docker-up      - Start PostgreSQL and Redis with docker-compose"
	@echo "  make docker-down    - Stop docker containers"

install:
	@if command -v poetry > /dev/null; then \
		poetry install; \
	else \
		pip install -r requirements.txt; \
	fi

run:
	@if command -v poetry > /dev/null; then \
		poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	fi

test:
	@if command -v poetry > /dev/null; then \
		poetry run pytest; \
	else \
		pytest; \
	fi

test-cov:
	@if command -v poetry > /dev/null; then \
		poetry run pytest --cov=app --cov-report=html --cov-report=term; \
	else \
		pytest --cov=app --cov-report=html --cov-report=term; \
	fi

lint:
	@if command -v poetry > /dev/null; then \
		poetry run ruff check app tests; \
	else \
		ruff check app tests; \
	fi

format:
	@if command -v poetry > /dev/null; then \
		poetry run black app tests; \
	else \
		black app tests; \
	fi

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage

migrate-create:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Please provide a migration message. Usage: make migrate-create msg='description'"; \
		exit 1; \
	fi
	@if command -v poetry > /dev/null; then \
		poetry run alembic revision --autogenerate -m "$(msg)"; \
	else \
		alembic revision --autogenerate -m "$(msg)"; \
	fi

migrate-up:
	@if command -v poetry > /dev/null; then \
		poetry run alembic upgrade head; \
	else \
		alembic upgrade head; \
	fi

migrate-down:
	@if command -v poetry > /dev/null; then \
		poetry run alembic downgrade -1; \
	else \
		alembic downgrade -1; \
	fi

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "PostgreSQL and Redis are ready!"

docker-down:
	docker-compose down
