#!/bin/bash
# Script pour lancer la DB et le backend sur le même réseau Docker

NETWORK=terraharbor-net
DB_CONTAINER=terraharbor_db
DB_IMAGE=terraharbor_db_image
BACKEND_IMAGE=terraharbor_backend

# Crée le réseau s'il n'existe pas
docker network inspect $NETWORK >/dev/null 2>&1 || docker network create $NETWORK

# Lance la DB

docker run -d --network $NETWORK \
  --name $DB_CONTAINER \
  -e POSTGRES_DB=$POSTGRES_DB \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -p 5432:5432 \
  $DB_IMAGE

# Lance le backend

docker run -d --network $NETWORK \
  -e POSTGRES_DB=$POSTGRES_DB \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -e POSTGRES_HOST=$DB_CONTAINER \
  -p 8000:8000 \
  $BACKEND_IMAGE

echo "Containers lancés sur le réseau $NETWORK."
echo "Backend: http://localhost:8000/docs"
