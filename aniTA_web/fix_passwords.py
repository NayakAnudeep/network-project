import os
import django
import bcrypt

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import the database
from users.arangodb import db, authenticate_user

def fix_user_passwords():
    print("Fixing user passwords...")
    
    # Get all users
    users = list(db.collection('users').all())
    print(f"Found {len(users)} users")
    
    # Set password to 'password' for all users
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    for user in users:
        user['password_hash'] = hashed_password
        db.collection('users').update(user)
        print(f"Updated password for {user.get('username')} ({user.get('email')})")
    
    # Test authentication with a sample user
    if users:
        sample_user = users[0]
        email = sample_user.get('email')
        print(f"\nTesting authentication for {email}...")
        result = authenticate_user(email, password)
        print(f"Authentication result: {result}")

if __name__ == "__main__":
    fix_user_passwords()