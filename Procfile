web: cd social_media && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn social_media.wsgi:application --bind 0.0.0.0:$PORT
