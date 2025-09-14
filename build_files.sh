#!/bin/bash

# Build script for Vercel deployment
echo "Building Django project for Vercel..."

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project directory
cd social_media

# Collect static files
python manage.py collectstatic --noinput --clear

# Create staticfiles_build directory and copy files
mkdir -p ../staticfiles_build
cp -r staticfiles/* ../staticfiles_build/

echo "Build completed successfully!"
