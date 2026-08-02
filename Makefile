.PHONY: help install dev up down logs \
	backend-install backend-dev backend-test backend-lint backend-format backend-typecheck backend-migrate backend-migration \
	frontend-install frontend-dev frontend-test frontend-lint frontend-format \
	test lint format clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: backend-install frontend-install ## Install all dependencies

dev: ## Start Postgres + Redis, then remind how to run the apps
	docker compose up -d postgres redis
	@echo "Now run 'make backend-dev' and 'make frontend-dev' in separate terminals."

up: ## Start the full stack in Docker
	docker compose up --build

down: ## Stop the full stack
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

# ---- Backend ----

backend-install: ## Create backend virtualenv and install dependencies
	cd backend && python3.13 -m venv .venv
	cd backend && .venv/bin/pip install --upgrade pip
	cd backend && .venv/bin/pip install -e ".[dev]"

backend-dev: ## Run the backend dev server with autoreload
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test: ## Run backend test suite
	cd backend && .venv/bin/pytest

backend-lint: ## Lint backend with Ruff and check formatting with Black
	cd backend && .venv/bin/ruff check .
	cd backend && .venv/bin/black --check .
	cd backend && .venv/bin/mypy app

backend-format: ## Auto-format backend code
	cd backend && .venv/bin/ruff check --fix .
	cd backend && .venv/bin/black .

backend-migrate: ## Apply database migrations
	cd backend && .venv/bin/alembic upgrade head

backend-migration: ## Create a new migration: make backend-migration name="add users table"
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(name)"

# ---- Frontend ----

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Run the frontend dev server
	cd frontend && npm run dev

frontend-test: ## Run frontend test suite
	cd frontend && npm run test

frontend-lint: ## Lint and type-check the frontend
	cd frontend && npm run lint
	cd frontend && npm run typecheck

frontend-format: ## Auto-format frontend code
	cd frontend && npm run format

# ---- Combined ----

test: backend-test frontend-test ## Run all test suites

lint: backend-lint frontend-lint ## Run all linters

format: backend-format frontend-format ## Auto-format all code

clean: ## Remove build artifacts and dependency caches
	rm -rf backend/.venv backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/htmlcov
	rm -rf frontend/node_modules frontend/dist frontend/coverage
