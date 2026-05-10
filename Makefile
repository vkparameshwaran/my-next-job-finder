.PHONY: help install dev dev-backend dev-frontend test test-backend test-frontend lint lint-backend lint-frontend fmt fmt-backend fmt-frontend typecheck precommit clean

help:
	@echo "Targets:"
	@echo "  install         Install backend + frontend deps and pre-commit hooks"
	@echo "  dev             Run backend (:8000) + frontend (:5173) concurrently"
	@echo "  dev-backend     Run only the backend"
	@echo "  dev-frontend    Run only the frontend"
	@echo "  test            Run all tests"
	@echo "  lint            Run all linters"
	@echo "  fmt             Format Python and TypeScript"
	@echo "  typecheck       Run mypy and tsc"
	@echo "  precommit       Run pre-commit against all files"
	@echo "  clean           Remove build artifacts and caches"

install:
	cd backend && uv sync --all-extras --dev
	cd frontend && pnpm install
	pre-commit install

dev:
	@echo "Starting backend on :8000 and frontend on :5173 ..."
	@(cd backend && uv run uvicorn app.main:app --reload --port 8000) & \
	 (cd frontend && pnpm dev) ; \
	 wait

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && pnpm dev

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest --cov=app --cov-report=term

test-frontend:
	cd frontend && pnpm test --run

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run ruff check . && uv run ruff format --check .

lint-frontend:
	cd frontend && pnpm lint

typecheck:
	cd backend && uv run mypy app
	cd frontend && pnpm typecheck

fmt: fmt-backend fmt-frontend

fmt-backend:
	cd backend && uv run ruff format . && uv run ruff check --fix .

fmt-frontend:
	cd frontend && pnpm format

precommit:
	pre-commit run --all-files

clean:
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/.coverage backend/coverage.xml backend/htmlcov
	rm -rf frontend/dist frontend/coverage frontend/.eslintcache frontend/node_modules/.cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
