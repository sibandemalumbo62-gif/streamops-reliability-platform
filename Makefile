.PHONY: help build up down restart logs test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-%: ## Show logs from specific service (make logs-auth)
	docker-compose logs -f $*

test: ## Run all tests
	@echo "Running Auth Service tests..."
	cd services/auth_service && pytest app/tests/ -v
	@echo "Running Catalog Service tests..."
	cd services/catalog_service && pytest app/tests/ -v
	@echo "Running Playback Service tests..."
	cd services/playback_service && pytest app/tests/ -v
	@echo "Running Recommendation Service tests..."
	cd services/recommendation_service && pytest app/tests/ -v
	@echo "Running Notification Service tests..."
	cd services/notification_service && pytest app/tests/ -v

migrate: ## Run database migrations
	@echo "Running migrations for all services..."
	cd services/auth_service && alembic upgrade head || true
	cd services/catalog_service && alembic upgrade head || true
	cd services/playback_service && alembic upgrade head || true
	cd services/recommendation_service && alembic upgrade head || true
	cd services/notification_service && alembic upgrade head || true
	cd services/integrity_service && alembic upgrade head || true

clean: ## Remove all containers, volumes, and networks
	docker-compose down -v
	docker system prune -f

install: ## Install dependencies for all services
	@echo "Installing dependencies..."
	cd services/auth_service && pip install -r requirements.txt
	cd services/catalog_service && pip install -r requirements.txt
	cd services/playback_service && pip install -r requirements.txt
	cd services/recommendation_service && pip install -r requirements.txt
	cd services/notification_service && pip install -r requirements.txt
	cd services/integrity_service && pip install -r requirements.txt
	cd gateway && pip install -r requirements.txt

dev: ## Start services in development mode
	@echo "Starting services in development mode..."
	docker-compose up --build

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "Gateway: Unavailable"
	@curl -s http://localhost:8001/health | jq . || echo "Auth Service: Unavailable"
	@curl -s http://localhost:8002/health | jq . || echo "Catalog Service: Unavailable"
	@curl -s http://localhost:8003/health | jq . || echo "Playback Service: Unavailable"
	@curl -s http://localhost:8004/health | jq . || echo "Recommendation Service: Unavailable"
	@curl -s http://localhost:8005/health | jq . || echo "Notification Service: Unavailable"
	@curl -s http://localhost:8006/ | jq . || echo "Integrity Service: Unavailable"
