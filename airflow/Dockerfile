# Or your preferred Airflow version
FROM apache/airflow:2.9.2 

# setthe airflow user
USER ${AIRFLOW_UID:-1000} 

RUN pip install confluent-kafka yfinance backtrader backtrader[plotting] python-binance
