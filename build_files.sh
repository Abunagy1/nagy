# build_files.sh
#!/bin/bash
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt
echo "Collecting static files..."
python3 manage.py collectstatic --noinput