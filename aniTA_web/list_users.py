#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from django.contrib.auth.models import User

def list_users():
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f" - {user.username} (Superuser: {user.is_superuser})")

if __name__ == "__main__":
    list_users()