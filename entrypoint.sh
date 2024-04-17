#!/bin/bash

# Load data from groups.json
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata groups.json
python3 manage.py createsuperuser --noinput

# Run the original command (e.g., Gunicorn)
exec "$@"