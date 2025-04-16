from arango import ArangoClient
from django.conf import settings
import bcrypt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create ArangoDB client
try:
    # Print connection info for debugging
    print(f"Connecting to: {settings.ARANGO_DB['HOST']}")
    
    # Create the client
    client = ArangoClient(hosts=settings.ARANGO_DB['HOST'])
    
    # Connect to the database
    db = client.db(
        name=settings.ARANGO_DB['DATABASE'],
        username=settings.ARANGO_DB['USERNAME'],
        password=settings.ARANGO_DB['PASSWORD'],
        verify=settings.ARANGO_DB['VERIFY_SSL']
    )
    
    logger.info(f"Connected to ArangoDB at {settings.ARANGO_DB['HOST']}")
    
except Exception as e:
    print(f"Detailed connection error: {str(e)}")
    logger.error(f"Failed to connect to ArangoDB: {str(e)}")
    # Re-raise the exception
    raise


# Your existing functions remain the same
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
    return {"success": "User registration successful"}

def authenticate_user(email, password):
    users = db.collection('users')
    user_list = list(users.find({'email': email}))
    if user_list:
        user = user_list[0]
        if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode("utf-8")):
            return {"failure": None, "user_id": user["_id"], "username": user["username"]}
        else:
            return {"failure": "Invalid credentials" }
    return {"failure": "Invalid credentials"}
