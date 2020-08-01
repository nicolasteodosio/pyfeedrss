include .env
export $(shell sed 's/=.*//' .env)

# TEXT/COLORS
GREEN:=$(shell tput setaf 2)
BOLD:=$(shell tput bold)
RESET:=$(shell tput sgr0)

# MESSAGES
SUCCESS_MESSAGE:=OK
SUCCESS:=$(GREEN)$(SUCCESS_MESSAGE)$(RESET)


env-switch-dev:
	@echo "switching to DEV..."
	@cp .env.dev .env


env-switch-prod:
	@echo "switching to PROD..."
	@cp .env.production .env

.PHONY: clean help

help:
	@echo "$(BOLD)clear$(RESET): clean temp files"
	@echo ""
	@echo "$(BOLD)install$(RESET):  ($(BOLD)$(GREEN)recommended$(RESET))."
	@echo ""
	@echo "$(BOLD)packages$(RESET): install project dependencies"
	@echo "$(BOLD)packages-dev$(RESET): install project dependencies for development"
	@echo "$(BOLD)docker-up$(RESET): run docker-compose."
	@echo "$(BOLD)docker-down$(RESET): down docker-compose."
	@echo ""
	@echo "$(BOLD)test$(RESET): run project tests."
	@echo "$(BOLD)coverage$(RESET): run project tests with coverage."
	@echo "$(BOLD)run-server$(RESET): run django dev server."
	@echo "$(BOLD)run-workers$(RESET): run dramatiq workers."
	@echo ""
	@echo "$(BOLD)help$(RESET): show this message."

clear:
	@printf "Cleaning temp files... "
	@rm -f dist/*.gz
	@rm -rfd *.egg-info
	@find . -type f -name '*.pyc' -delete
	@find . -type f -name '*.log' -delete
	@echo "$(SUCCESS)"


packages-dev:
	@printf "Installing dev dependencies... "
	@pip install -q --no-cache-dir -r requirements/dev.txt
	@echo "$(SUCCESS)"

packages:
	@printf "Installing dependencies... "
	@pip install -q --no-cache-dir -r requirements/base.txt
	@echo "$(SUCCESS)"


docker-up:
	@docker-compose --log-level ERROR up -d

docker-down:
	@docker-compose down

install-git-hooks:
	@pre-commit install

install: clear packages-dev install-git-hooks
	@echo "============================================"
	@echo "All done for development"
	@echo "============================================"

test:
	@pytest -xv

coverage:
	@pytest -xv --cov=app --cov-report term-missing

run-migrations:
	@python  manage.py migrate --settings=pyfeedrss.settings.local

run-server:
	@python  manage.py runserver --settings=pyfeedrss.settings.local

run-workers:
	@python  manage.py rundramatiq
