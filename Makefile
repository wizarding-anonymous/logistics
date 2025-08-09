# Makefile for managing the local development environment

# Default command
.DEFAULT_GOAL := help

# Environment variables
-include .env
export

# Commands
.PHONY: help up down stop logs ps build restart init

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services in detached mode
	@echo "Starting local environment..."
	docker compose up -d

down: ## Stop and remove all containers, networks, and volumes
	@echo "Stopping local environment..."
	docker compose down --volumes

stop: ## Stop all services
	@echo "Stopping services..."
	docker compose stop

logs: ## Follow logs of all services
	@echo "Following logs..."
	docker compose logs -f

ps: ## List running services
	@echo "Current status:"
	docker compose ps

build: ## Build or rebuild service images
	@echo "Building images..."
	docker compose build

restart: ## Restart all services
	@echo "Restarting services..."
	make stop
	make up

init: ## Initialize the environment (e.g., create buckets, topics)
	@echo "Initializing environment..."
	# Placeholder for initial setup scripts
	# Example: docker compose exec minio mc mb local/my-bucket
	# Example: docker compose exec kafka kafka-topics --create ...
	@echo "Initialization complete."
