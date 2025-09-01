#! /bin/bash

# Create database and user in database using the superuser role.
psql --username postgres \
  --dbname $TERRAHARBOR_DB_NAME \
  --variable db_name=$TERRAHARBOR_DB_NAME \
  --variable db_user=$TERRAHARBOR_DB_USER \
  --variable db_password=$TERRAHARBOR_DB_PASSWORD \
  --file /db-init-scripts/base.sql

# Create the tables.
psql --dbname $TERRAHARBOR_DB_NAME --username postgres --file /db-init-scripts/tables.sql
