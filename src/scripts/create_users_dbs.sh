#!/bin/bash

# Connect to the default database (`postgres`) as the superuser.
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    -- Check if the 'postgres' user exists, create if not.
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
            CREATE ROLE postgres WITH LOGIN PASSWORD 'billna1';
        END IF;
    END
    \$\$;

    -- Check if the 'trading_data' database exists, create if not.
    SELECT 'CREATE DATABASE trading_data OWNER postgres'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'trading_data')\gexec

    -- Check if the 'airflow' user exists, create if not.
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
            CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow';
        END IF;
    END
    \$\$;

    -- Check if the 'airflow' database exists, create if not.
    SELECT 'CREATE DATABASE airflow OWNER airflow'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
EOSQL