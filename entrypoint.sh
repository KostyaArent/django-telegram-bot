#!/bin/sh

# Apply database migrations
echo "Applying database migrations ..."
python manage.py migrate

# Adding games to base
echo "Adding games to database ..."
python manage.py shell games_add_to_base.py
# Create superuser
echo "Creating superuser ..."
python manage.py createsuperuser --noinput

# Load initial data (fixtures)
echo "Load initial data"
# python manage.py loaddata MyFixture.json

# Collecting static
echo "Collecting static ..."
python manage.py collectstatic

# Start server
echo "Starting server ..."
python manage.py runserver 0.0.0.0:8000
