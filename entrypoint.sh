#!/bin/bash

# Attendre que la base de données soit prête
echo "Waiting for postgres..."

# Utiliser des valeurs par défaut si les variables ne sont pas définies
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "Connecting to $DB_HOST:$DB_PORT"

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Appliquer les migrations
echo "Applying database migrations..."
python manage.py migrate

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Créer un superutilisateur si les variables sont définies
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

# Exécuter la commande passée en argument
exec "$@"
