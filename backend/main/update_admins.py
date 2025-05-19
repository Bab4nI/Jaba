import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from registration.models import User

def update_admin_groups():
    admin_users = User.objects.filter(role='admin')
    updated_count = 0
    
    for user in admin_users:
        if user.group != 'admins':
            user.group = 'admins'
            user.save()
            updated_count += 1
            print(f"Updated user: {user.username}")
    
    print(f"\nTotal admin users: {admin_users.count()}")
    print(f"Updated users: {updated_count}")

if __name__ == '__main__':
    update_admin_groups() 