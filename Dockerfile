FROM postgres:latest AS builder
RUN apt-get update && apt-get install -y postgresql-client
# Extract pg_config to a known location
RUN cp /usr/lib/postgresql/16/bin/pg_config /pg_config

FROM python:3.10-slim-buster

COPY --from=builder /pg_config /usr/local/bin/pg_config

WORKDIR /app

RUN pip install psycopg2-binary

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

RUN python3 manage.py collectstatic --no-input


ENV POSTGRES_DB=delivery_tracking_db
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=wolcott123!
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "delivery_tracking.wsgi:application"]

