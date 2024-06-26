.PHONY: run-dev down clean build up build-pipeline run test test_db create_trading_database build-base-image build-base-image-restart d-% up-% run-% logs-% build-% bash-% save-strategies create-superuser drop-user create-db drop-db init-db build-all setup-trading-db start

# Makefile for managing PostgreSQL users in Docker

POSTGRES_CONTAINER := postgres  # Adjust if your container name is different
POSTGRES_MAIN_USER := airflow
POSTGRES_USER := postgres

start:
	make build-base-image
	make build-all
	export PYTHONPATH=$PYTHONPATH:$(pwd)
	make up
	make setup-trading-db
	alembic upgrade head
	make save-strategies


save-strategies:
	python backtest_service/scripts/save_strategies.py

setup-trading-db:
	make create-superuser
	make create-db
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -d trading_data -c "\
	make clean-trading-data-tables;"

clean-trading-data-tables:
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -d trading_data -c "\
	DO \
	$$ \
	DECLARE \
			stmt TEXT; \
	BEGIN \
			FOR stmt IN \
					SELECT 'DROP TABLE IF EXISTS ' || quote_ident(table_schema) || '.' || quote_ident(table_name) || ' CASCADE;' \
					FROM information_schema.tables \
					WHERE table_schema = 'public' \
			LOOP \
					EXECUTE stmt; \
			END LOOP; \
	END \
	$$;"  # End of SQL command

create-superuser:
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_MAIN_USER) -f create_superuser.sql

drop-user:
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_MAIN_USER) -c "DROP USER postgres;"

# Create a database trading data
create-db:
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -c "CREATE DATABASE trading_data;"

# Drop the trading data database
drop-db:
	docker compose exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -c "DROP DATABASE IF EXISTS trading_data;"

make init-db:
	make create-superuser
	make create-db

build-all:
	docker compose build

run:
	make down
	make up

run-dev:
	fastapi dev api/main.py

# build-api:
# 	docker compose build api
# 	make up

build-pipeline:
	docker compose build data-pipeline
	make up

up:
	docker compose up -d

down:
	docker compose down

test:
	pytest -v -s tests
	
clean:
	make down
	docker volume rm $(shell docker volume ls -qf dangling=true)
	docker rmi $(shell docker images -qf dangling=true)

test_db:
	@for i in `seq 1 5`; do \
		if (docker compose exec postgres sh -c 'psql -U postgres -c "select 1;"' 2>&1 > /dev/null) then break; \
		else echo "postgres initializing..."; sleep 5; fi \
	done
	docker compose exec postgres sh -c 'psql -U postgres -c "drop database if exists tests;" && psql -U postgres -c "create database tests;"'

create_trading_database:
	docker compose exec -u postgres postgres psql postgres -c "CREATE DATABASE trading_data;"

build-base-image:
	docker build -t base-image-gold -f Dockerfile.base .

build-base-image-restart:
	make build-base-image
	make build-all
	make run

# Command to stop the container passed in to replace % with the container name
d-%:
	docker compose down $*

up-%:
	docker compose up -d $*

run-%:
	make d-$*
	make up-$*

logs-%:
	docker compose logs -f $*

build-%:
	docker compose build $* --no-cache
	docker compose up -d $*
	docker compose logs -f $*

bash-%:
	docker compose exec $* bash

	