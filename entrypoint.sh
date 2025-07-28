#!/bin/bash

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de la base de données..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ Base de données prête!"

# Migrer la base de données
echo "🔄 Migration de la base de données..."
python manage.py migrate

# Créer un superutilisateur si il n'existe pas
echo "👤 Configuration du superutilisateur..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME:-admin}', '${DJANGO_SUPERUSER_EMAIL:-admin@example.com}', '${DJANGO_SUPERUSER_PASSWORD:-admin123}') if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME:-admin}').exists() else print('Superutilisateur existe déjà')" | python manage.py shell

echo "🚀 Démarrage du serveur Django..."
exec "$@"