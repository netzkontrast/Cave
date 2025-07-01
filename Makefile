.PHONY: help install run lint format test clean db-init venv fresh-install

help: ## Show this help message
	@echo "Cave - Character Interaction System (venv/pip version)"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create a virtual environment in .venv
	python3 -m venv .venv

fresh-install: ## Remove .venv and recreate it with fresh dependencies
	@echo "Removing existing virtual environment..."
	rm -rf .venv
	@echo "Creating fresh virtual environment..."
	python3 -m venv .venv
	@echo "Installing dependencies..."
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Fresh installation complete!"

install: venv ## Install dependencies using pip
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

run: ## Run the backend server
	.venv/bin/python start_backend.py

run-backend: ## Run the backend server (alias for run)
	.venv/bin/python start_backend.py

lint: ## Run linting checks
	.venv/bin/flake8 backend/
	.venv/bin/mypy backend/
	.venv/bin/isort --check-only backend/

format: ## Format code with black and isort
	.venv/bin/black backend/
	.venv/bin/isort backend/

test: ## Run tests
	.venv/bin/pytest

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage

db-init: ## Initialize the database
	.venv/bin/python -c "from backend.database import create_tables, init_db; create_tables(); init_db()" 