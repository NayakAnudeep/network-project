
# 🌍 Project URL Configuration (`urls.py`)

## 📌 Overview
This file defines the **main URL routing** for the Django project. It includes **app-specific URL configurations** and the **Django admin panel**.

---

## 🔹 Importing Required Modules
```python
from django.contrib import admin
from django.urls import include, path
```
- `admin`: Enables Django's built-in **admin interface**.
- `include`: Allows including **URL configurations from other apps**.
- `path`: Defines individual URL patterns.

---

## 🔹 Defining URL Patterns
```python
urlpatterns = [
    path('', include("aniTA_app.urls")),
    path('users/', include("users.urls")),
    path('admin/', admin.site.urls),
]
```

### 📌 **Explanation:**
| URL Path   | Included App  | Description |
|------------|--------------|-------------|
| `/`        | `aniTA_app`  | Routes all base URLs to `aniTA_app.urls`. |
| `/users/`  | `users`      | Routes all user-related URLs to `users.urls`. |
| `/admin/`  | Django Admin | Provides access to the **Django admin panel**. |


---

## 🔹 Example API Calls
### **1️⃣ Accessing the Main App**
```
GET http://localhost:8000/
```
If `aniTA_app.urls` is correctly configured, it will **handle the request**.

---

### **2️⃣ User API Requests**
#### **User Registration**
```
POST http://localhost:8000/users/register/
```
#### **User Login**
```
POST http://localhost:8000/users/login/
```
These routes **delegate handling** to `users.urls`.

---

### **3️⃣ Accessing Django Admin Panel**
Visit:
```
http://localhost:8000/admin/
```
Use your **superuser credentials** to log in.

---

## 🔹 Debugging & Testing
### **1️⃣ Check All Registered URLs**
```sh
python manage.py show_urls
```

### **2️⃣ Ensure Apps Are Loaded Correctly**
```sh
python manage.py check
```
If there are missing **URL configurations**, this command will report them.

### **3️⃣ Testing with cURL**
#### **Check User API Route**
```sh
curl -X GET http://localhost:8000/users/
```
If correctly configured, this will return a **valid response**.

---

🎯 **Your Django URL configuration is now fully documented!** 🚀

