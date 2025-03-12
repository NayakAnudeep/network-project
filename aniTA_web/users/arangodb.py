
from arango import ArangoClient
from django.conf import settings
import bcrypt
from datetime import datetime

# Construct the full ArangoDB connection URL
arangodb_url = f"{settings.ARANGO_DB['HOST']}:{settings.ARANGO_DB['PORT']}"

# Initialize the ArangoDB client with the full URL
client = ArangoClient(hosts=arangodb_url)

# Ensure the database exists before using it
sys_db = client.db("_system", username=settings.ARANGO_DB['USERNAME'], password=settings.ARANGO_DB['PASSWORD'])
if not sys_db.has_database(settings.ARANGO_DB['DATABASE']):
    sys_db.create_database(settings.ARANGO_DB['DATABASE'])

# Now connect to the correct database
db = client.db(settings.ARANGO_DB['DATABASE'], 
               username=settings.ARANGO_DB['USERNAME'], 
               password=settings.ARANGO_DB['PASSWORD'])

# Check if the 'users' collection exists, create if missing
if not db.has_collection('users'):
    db.create_collection('users')

# Function to create a new user
def register_user(username, email, password, role="student"):
    users = db.collection('users')

    # Check if the email already exists
    existing_user = list(users.find({"email": email}))
    if existing_user:
        return {"error": "User already exists"}

    # Hash the password
    hashed_pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user data
    user_data = {
        "username": username, 
        "email": email, 
        "password_hash": hashed_pswd.decode('utf-8'), 
        "role": role, 
        "created_at": datetime.utcnow().isoformat()
    }

    users.insert(user_data)
    return {"message": "User registration successful"}

# Function to authenticate user
def authenticate_user(email, password):
    users = db.collection('users')
    user_list = list(users.find({'email': email}))

    if user_list:  # Ensure user_list is not empty
        user = user_list[0]
        if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode("utf-8")):
            return {"message": "Authentication successful", "user": user}
    
    return {"error": "Invalid credentials"}

