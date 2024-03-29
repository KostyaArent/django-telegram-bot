#!/bin/sh

# Apply database migrations
echo "Applying database migrations ..."
#python manage.py makemigrations --noinput && 
python manage.py migrate

# Create superuser
echo "Creating superuser ..."
python manage.py createsuperuser --noinput

# Adding games to base
# echo "Adding empl_values to database ..."
# python manage.py runscript tgbot_empl_val_add_to_base --dir-policy each

# Load initial data (fixtures)
# echo "Load initial data"
# python manage.py loaddata MyFixture.json

# Collecting static
echo "Collecting static ..."
python manage.py collectstatic

# Start server
echo "Starting server ..."
python manage.py runserver 0.0.0.0:8000
