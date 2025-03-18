#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  echo "🟡 Waiting for MySQL Database Startup ($MYSQL_HOST $MYSQL_PORT) ..."
  sleep 2
done

echo "✅ MySQL Database Started Successfully ($MYSQL_HOST:$MYSQL_PORT)"

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py seed leads --number=50
python manage.py runserver 0.0.0.0:8000
