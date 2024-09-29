#!/bin/sh

# Make migrations and migrate the database.
echo "Making migrations and migrating the database. "
python manage.py makemigrations --noinput
python3 manage.py migrate --noinput --run-syncdb
python manage.py collectstatic --noinput
exec "$@"