# Crypto Trading Engineering: Scalable Backtesting Infrastructure

[![Build Status](https://github.com/10ac-week9-group4/Backtesting-Infrastructure-CryptoTrading/actions/workflows/main.yml/badge.svg)](https://github.com/10ac-week9-group4/Backtesting-Infrastructure-CryptoTrading/actions/workflows/main.yml)

## Overview

This project is a robust trading and backtesting infrastructure designed to support the evaluation of various trading strategies on financial instruments like stocks and cryptocurrencies. It leverages a microservices architecture with Docker for flexibility and scalability, using tools like Airflow, Kafka, FastAPI, and PostgreSQL.

## Key Features

- **Automated Data Pipeline:** Fetches historical market data using `yfinance`, processes it, and stores it in a PostgreSQL database.
- **Backtesting Engine:**  Evaluates trading strategies against historical or real-time market data.
- **Strategy Management:** Allows the creation and storage of custom trading strategies.
- **Kimball Schema:** Employs a Kimball data warehouse schema for efficient storage and analysis of data.
- **Microservice Architecture:**  Utilizes Docker containers for modularity and scalability.
- **Kafka Integration:** Employs Kafka for real-time data streaming and message passing.
- **FastAPI Backend:** Provides a modern REST API for interacting with the system.
- **WebSocket Support:** Enables real-time updates and data streaming to the frontend.
- **Scalability:** Designed to handle increasing volumes of data and backtest scenarios.


## Project Structure

- `airflow/`: Contains Airflow DAGs for orchestrating data pipelines and backtests.
- `api/`: Houses the FastAPI backend service.
- `database_service/`: Contains the database service logic for data access and storage.
- `kafka_consumer/`: Holds the Kafka consumer service for data ingestion.
- `models/`: Defines the SQLAlchemy models for the database schema.
- `shared/`:  Stores shared modules (e.g., utility functions, configurations).
- `src/`:  Contains source code for data fetching, backtesting logic, and strategies.
- `tests/`: Includes unit and integration tests for the project.

## Getting Started

1. **Prerequisites:**
   - Docker and Docker Compose
   - Python 3.9+ (with required dependencies: see `requirements.txt`)

## Installation

- Fork the repository
- Clone the repository you just forked using `git clone`

In your terminal:

```bash
cd Backtesting-Infrastructure-CryptoTrading
pip install -r requirements.txt
```

## Usage

In your terminal run:

```bash
make up
```

This will start the services in compose.yaml file. You can check the status of
the services by running:

```bash
docker ps
```

To check the logs of a service, run:

```bash
docker compose logs -f <service_name>
```
  Where the service_name is the name of the service found in the compose.yaml
file.

* Example of checking the logs of the api service:

  ```bash
  docker compose logs -f api
  ```

## Accessing Services
   - Airflow UI:  http://localhost:8080
   - FastAPI Docs: http://localhost:8089/docs 
   - Database Service: http://localhost:8001
   - Kafka Consumer: logs can be viewed using `docker compose logs -f kafka-consumer`


## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
