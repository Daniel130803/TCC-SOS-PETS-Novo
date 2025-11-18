# S.O.S Pets - Makefile (atalhos úteis)
# Use: make <comando>

.PHONY: help install dev docker-up docker-down docker-logs test lint format clean

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências Python
	cd backend/backend && pip install -r requirements.txt

dev: ## Roda servidor de desenvolvimento
	cd backend/backend && python manage.py runserver

docker-up: ## Sobe containers Docker
	docker-compose up -d

docker-down: ## Para containers Docker
	docker-compose down

docker-logs: ## Mostra logs dos containers
	docker-compose logs -f web

docker-build: ## Reconstrói imagens Docker
	docker-compose build

docker-shell: ## Acessa shell do container web
	docker-compose exec web bash

migrate: ## Roda migrações do banco
	cd backend/backend && python manage.py migrate

makemigrations: ## Cria novas migrações
	cd backend/backend && python manage.py makemigrations

superuser: ## Cria superusuário
	cd backend/backend && python manage.py createsuperuser

test: ## Roda testes
	cd backend/backend && python manage.py test

lint: ## Verifica qualidade do código
	cd backend/backend && ruff check . && black --check . && isort --check-only .

format: ## Formata código automaticamente
	cd backend/backend && black . && isort .

clean: ## Remove arquivos temporários
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
