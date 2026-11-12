#!/bin/bash
set -e

psql \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=db_name="$DB_NAME" \
    --set=db_user="$DB_USER" \
    --set=db_password="$DB_PASSWORD" \
    --file=/docker/postgres/sql/01-create-app-database.sql

psql \
    --username "$POSTGRES_USER" \
    --dbname "$DB_NAME" \
    --file=/docker/postgres/sql/02-create-tables.sql