# account/management/commands/create_superuser_from_env.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser from environment variables'

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')

        if not email or not password:
            self.stdout.write(self.style.WARNING('Superuser environment variables not set. Skipping.'))
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password, username=username)
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))