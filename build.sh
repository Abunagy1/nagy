#!/bin/bash
echo "Starting build.sh..."

# echo "Upgrading pip and setuptools..."
# python3 -m pip install --break-system-packages --upgrade pip setuptools

# echo "Installing Python dependencies..."
# python3 -m pip install --break-system-packages --upgrade -r requirements.txt

echo "Installing Python dependencies with upgrade strategy..."
python3 -m pip install --break-system-packages --upgrade --upgrade-strategy eager -r requirements.txt

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Creating superuser from environment..."
python3 manage.py create_superuser_from_env

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Build completed."