# TODO REALLY VULNERABLE
FROM postgres:16.3

# Set environment variables for default database and user
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Expose PostgreSQL port
EXPOSE 5432

# Optional: Add initialization scripts
# COPY ./init.sql /docker-entrypoint-initdb.d/