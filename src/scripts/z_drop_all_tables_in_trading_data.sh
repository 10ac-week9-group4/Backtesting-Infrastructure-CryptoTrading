#!/bin/bash
set -e

# Wait for Postgres to start
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Execute the SQL script to drop all tables in the trading_data database
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "trading_data" -f /docker-entrypoint-initdb.d/drop_all_tables_in_trading_data.sql