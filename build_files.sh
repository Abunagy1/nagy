#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt

echo "Running database migrations..."
python3 manage.py migrate --noinput

python3 manage.py create_superuser_from_env

echo "Collecting static files..."
python3 manage.py collectstatic --noinput