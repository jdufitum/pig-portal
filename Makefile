ENV_FILE?=.env

.PHONY: up down logs ps build backup restore

up:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml up -d --build
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml ps

build:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml build

ps:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml ps

logs:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml logs -f

down:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml down

backup:
	docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml exec -T db pg_dump -U postgres -d pigs | gzip > backup_`date +%Y%m%d_%H%M%S`.sql.gz

restore:
	gunzip -c $(FILE) | docker compose --env-file $(ENV_FILE) -f infrastructure/docker-compose.yml exec -T db psql -U postgres -d pigs