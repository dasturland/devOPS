# TableReserve — developer task runner.
# Usage: `make <target>`. See `make help` for the list.

.DEFAULT_GOAL := help
PYTHON ?= python
MANAGE := $(PYTHON) manage.py

.PHONY: help install migrate makemigrations seed run lint format typecheck test diagrams \
        docker-build docker-up docker-down clean

help: ## Ushbu yordamni ko'rsatish
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Dev bog'liqliklarni o'rnatish
	$(PYTHON) -m pip install -r requirements/dev.txt

migrate: ## Migratsiyalarni qo'llash
	$(MANAGE) migrate

makemigrations: ## Migratsiya fayllarini yaratish
	$(MANAGE) makemigrations

seed: ## Demo ma'lumotlarni yuklash (idempotent)
	$(MANAGE) seed_demo_data

run: ## Dev serverni ishga tushirish
	$(MANAGE) runserver

lint: ## ruff bilan lint + format tekshiruvi
	ruff check .
	ruff format --check .

format: ## ruff bilan formatlash va autofix
	ruff format .
	ruff check --fix .

typecheck: ## mypy bilan tiplarni tekshirish
	mypy apps config

test: ## Testlarni qamrov bilan ishga tushirish
	pytest --cov

diagrams: ## UML diagrammalarni Kroki orqali render qilish
	$(PYTHON) scripts/render_diagrams.py

docker-build: ## Docker image build qilish
	docker compose build

docker-up: ## Docker Compose stekini ishga tushirish
	docker compose up -d --build

docker-down: ## Docker Compose stekini to'xtatish
	docker compose down

clean: ## Keshlarni tozalash
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage coverage.xml
