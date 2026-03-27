# Solvia Labs website — common dev commands
# Requires: make, Python 3, Docker (for local Postgres). On Windows, use Git Bash or WSL for best compatibility.

.PHONY: help backend-install backend-dev backend-test db-up db-down db-migrate db-psql jekyll-build jekyll-serve bundle-install clean

PYTHON ?= python
BACKEND := backend
COMPOSE := docker compose -f docker-compose.postgres.yml
SQL_FILE := $(BACKEND)/sql/001_lead_audits.sql

# Interpreter inside backend/.venv (paths relative to backend/ after cd)
ifeq ($(OS),Windows_NT)
  VENV_REL := .venv/Scripts/python.exe
else
  VENV_REL := .venv/bin/python
endif

help:
	@echo "Solvia Labs — common commands"
	@echo ""
	@echo "  make backend-install   Create backend/.venv and pip install -r requirements.txt"
	@echo "  make backend-dev       Run FastAPI (uvicorn) on http://127.0.0.1:8000"
	@echo "  make backend-test      Run pytest in backend/"
	@echo "  make db-up             Start local Postgres (Docker)"
	@echo "  make db-down           Stop local Postgres"
	@echo "  make db-migrate        Apply sql/001_lead_audits.sql to local Postgres"
	@echo "  make db-psql           Open psql shell in the Postgres container"
	@echo "  make jekyll-build      bundle exec jekyll build"
	@echo "  make jekyll-serve      bundle exec jekyll serve (live reload)"
	@echo "  make bundle-install    bundle install (Ruby/Jekyll deps)"
	@echo "  make clean             Remove backend/.venv (needs rm: Git Bash/WSL)"
	@echo ""
	@echo "Set PYTHON=python3 if needed. Ensure backend/.env exists (copy from .env.example)."

backend-install:
	cd $(BACKEND) && $(PYTHON) -m venv .venv
	cd $(BACKEND) && $(VENV_REL) -m pip install -U pip
	cd $(BACKEND) && $(VENV_REL) -m pip install -r requirements.txt

backend-dev:
	cd $(BACKEND) && $(VENV_REL) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

backend-test:
	cd $(BACKEND) && $(VENV_REL) -m pytest tests/ -v

db-up:
	$(COMPOSE) up -d

db-down:
	$(COMPOSE) down

db-migrate:
	docker cp $(SQL_FILE) solvia-postgres:/tmp/001_lead_audits.sql
	docker exec solvia-postgres psql -U postgres -d solvia -v ON_ERROR_STOP=1 -f /tmp/001_lead_audits.sql

db-psql:
	docker exec -it solvia-postgres psql -U postgres -d solvia

bundle-install:
	bundle install

jekyll-build:
	bundle exec jekyll build

jekyll-serve:
	bundle exec jekyll serve

clean:
	rm -rf $(BACKEND)/.venv
