.PHONY: up down logs seed test lint fmt api-shell db-shell migrate revision web-install

# ---- Local stack ----
up:            ## Start postgres + api + web
	docker compose up --build -d

down:          ## Stop everything
	docker compose down

logs:          ## Tail all logs
	docker compose logs -f

# ---- Database ----
seed:          ## Seed employees & settings
	docker compose exec api python -m app.seed

migrate:       ## Apply migrations
	docker compose exec api alembic upgrade head

revision:      ## Create a new migration (msg="...")
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

db-shell:      ## psql into the dev database
	docker compose exec db psql -U hrms -d hrms

# ---- Quality ----
test:          ## Run backend tests
	docker compose exec api pytest -q

lint:          ## Lint backend + frontend
	docker compose exec api ruff check .
	docker compose exec web npm run lint

fmt:           ## Format backend
	docker compose exec api ruff format .

api-shell:     ## Shell into the api container
	docker compose exec api sh
