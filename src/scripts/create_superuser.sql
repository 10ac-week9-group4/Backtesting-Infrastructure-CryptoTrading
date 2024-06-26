DO $$ \
BEGIN \
  IF NOT EXISTS ( \
    SELECT FROM pg_catalog.pg_user \
    WHERE usename = 'postgres') THEN \
    CREATE USER postgres WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD 'billna1'; \
  END IF; \
END $$;"