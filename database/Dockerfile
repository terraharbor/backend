# TODO REALLY VULNERABLE
FROM postgres:17.6

# Set environment variables for default database and user
ENV POSTGRES_DB=$POSTGRES_DB
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# Expose PostgreSQL port
EXPOSE 5432

# Optional: Add initialization scripts
COPY ./init.sql /docker-entrypoint-initdb.d/
