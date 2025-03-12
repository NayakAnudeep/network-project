
# 🗄️ ArangoDB Integration Documentation

## 📌 Overview
This module (`arangodb.py`) handles the **ArangoDB connection, database creation, user management, and authentication**.

## 🔧 **ArangoDB Connection Setup**
The connection is established using `ArangoClient`. It reads the database credentials from `settings.py`.

### **Connection Code**
```python
from arango import ArangoClient
from django.conf import settings
```

### **Constructing Database URL**
```python
arangodb_url = f"{settings.ARANGO_DB['HOST']}:{settings.ARANGO_DB['PORT']}"
```

### **Initialize ArangoDB Client**
```python
client = ArangoClient(hosts=arangodb_url)
```

---

## 🔹 **Database and Collection Setup**
### **Ensure Database Exists**
The `_system` database is used to check if the target database exists. If not, it is created.
```python
sys_db = client.db("_system", username=settings.ARANGO_DB['USERNAME'], password=settings.ARANGO_DB['PASSWORD'])
if not sys_db.has_database(settings.ARANGO_DB['DATABASE']):
    sys_db.create_database(settings.ARANGO_DB['DATABASE'])
```

### **Connecting to the Target Database**
```python
db = client.db(settings.ARANGO_DB['DATABASE'],
               username=settings.ARANGO_DB['USERNAME'],
               password=settings.ARANGO_DB['PASSWORD'])
```

### **Ensure 'users' Collection Exists**
```python
if not db.has_collection('users'):
    db.create_collection('users')
```

---

## 👤 **User Management Functions**

### **🔹 Registering a New User**
```python
def register_user(username, email, password, role="student"):
```
#### **Steps:**
1. Check if the email already exists.
2. Hash the password securely.
3. Store user details in the `users` collection.

#### **Code Snippet:**
```python
existing_user = list(users.find({"email": email}))
if existing_user:
    return {"error": "User already exists"}

hashed_pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
user_data = {
    "username": username,
    "email": email,
    "password_hash": hashed_pswd.decode('utf-8'),
    "role": role,
    "created_at": datetime.utcnow().isoformat()
}
users.insert(user_data)
return {"message": "User registration successful"}
```

### **🔹 Authenticating a User**
```python
def authenticate_user(email, password):
```
#### **Steps:**
1. Retrieve user by email.
2. Verify the hashed password.
3. Return success or error message.

#### **Code Snippet:**
```python
user_list = list(users.find({'email': email}))
if user_list:
    user = user_list[0]
    if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode("utf-8")):
        return {"message": "Authentication successful", "user": user}
return {"error": "Invalid credentials"}
```

---

## 📜 **Testing and Debugging**
### **1️⃣ Checking Database Connection**
Inside the Django container:
```sh
docker exec -it web python manage.py shell
```
Run:
```python
from arango import ArangoClient
client = ArangoClient(hosts="http://arangodb:8529")
client.db("_system", username="root", password="aitaArango")
```
If the connection is successful, no errors will appear.

### **2️⃣ Checking the Debug Log**
```sh
docker exec -it web cat /tmp/debug_arangodb_url.txt
```

### **3️⃣ Manually Creating a User (Testing in Django Shell)**
```python
from users.arangodb import register_user
register_user("test_user", "test@example.com", "password123")
```

🎯 **Now your ArangoDB integration is fully functional!** 🚀

