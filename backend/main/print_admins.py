import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from registration.models import User

admins = User.objects.filter(role='admin')
print('Admins:', list(admins.values('id', 'email', 'group', 'is_active', 'first_name', 'last_name'))) 