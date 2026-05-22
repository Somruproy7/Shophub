web: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py import_from_mongo && gunicorn myecommerce.wsgi:application --bind 0.0.0.0:$PORT
