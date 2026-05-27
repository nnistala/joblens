.PHONY: dev dev-build down migrate seed crawl-greenhouse crawl-lever \
       test-backend test-frontend lint shell logs ps

# ── Docker Compose ────────────────────────────────────────────
dev:
	docker compose up

dev-build:
	docker compose up --build

down:
	docker compose down

down-v:
	docker compose down -v

ps:
	docker compose ps

logs:
	docker compose logs -f

# ── Database ──────────────────────────────────────────────────
migrate:
	docker compose exec api alembic upgrade head

migrate-generate:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec api python -m infra.scripts.seed_companies

seed-local:
	python infra/scripts/seed_companies.py

# ── Crawling ──────────────────────────────────────────────────
crawl-greenhouse:
	docker compose exec celery-worker celery -A tasks call tasks.crawl_tasks.run_tier1_crawls

crawl-lever:
	docker compose exec celery-worker celery -A tasks call tasks.crawl_tasks.run_tier2_crawls

# ── Testing ───────────────────────────────────────────────────
test-backend:
	docker compose exec api pytest -v

test-frontend:
	cd frontend && npm test

test: test-backend test-frontend

# ── Linting ───────────────────────────────────────────────────
lint:
	cd backend && ruff check .
	cd frontend && npx eslint src/

lint-fix:
	cd backend && ruff check --fix .
	cd frontend && npx eslint --fix src/

format:
	cd backend && ruff format .
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,js,jsx}"

# ── Shell Access ──────────────────────────────────────────────
shell:
	docker compose exec api bash

shell-db:
	docker compose exec postgres psql -U joblens -d joblens

shell-redis:
	docker compose exec redis redis-cli

# ── Setup ─────────────────────────────────────────────────────
setup:
	bash infra/scripts/setup_dev.sh
