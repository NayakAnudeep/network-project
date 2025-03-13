
# 🛠️ Django Settings Documentation (`settings.py`)

## 📌 Overview
The `settings.py` file configures the Django project, including **database settings, installed apps, middleware, and security configurations**.

---

## 🔹 Project Paths
```python
from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
```
- `BASE_DIR` is the root directory of the Django project.
- All file paths will be constructed relative to this directory.

---

## 🔹 Security Settings
```python
SECRET_KEY = 'django-insecure-$$aq%ljqn&#cz7of%ycoiq!d^c$4^@el_6n3j*9bj64*h3#-sr'
DEBUG = True
ALLOWED_HOSTS = []
```
- **`SECRET_KEY`**: Used for cryptographic signing. Change it for production.
- **`DEBUG`**: Should be **`False`** in production.
- **`ALLOWED_HOSTS`**: Define domains that can access the Django app.

---

## 🔹 Installed Apps
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'aniTA_app',
    'users',
]
```
- Contains built-in and custom apps.
- Custom apps include `aniTA_app` and `users`.

---

## 🔹 ArangoDB Configuration
```python
ARANGO_DB = {
    'HOST': os.getenv("ARANGO_DB_HOST", "http://arangodb"),
    'PORT': os.getenv("ARANGO_DB_PORT", "8529"),
    'USERNAME': os.getenv("ARANGO_DB_USER", "root"),
    'PASSWORD': os.getenv("ARANGO_DB_PASSWORD", "aitaArango"),
    'DATABASE': os.getenv("ARANGO_DB_NAME", "aita_db")
}
```
- Reads **database connection settings** from environment variables.
- Ensures **ArangoDB** connection is properly configured.

---

## 🔹 Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```
- Middleware handles **security, sessions, authentication, and request processing**.

---

## 🔹 URL and WSGI Configuration
```python
ROOT_URLCONF = 'aniTA_server.urls'
WSGI_APPLICATION = 'aniTA_server.wsgi.application'
```
- **`ROOT_URLCONF`**: Entry point for all Django URLs.
- **`WSGI_APPLICATION`**: Used for deploying Django applications.

---

## 🔹 Database Configuration (Default SQLite)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
- Uses **SQLite3** by default. Can be changed to **PostgreSQL, MySQL, or ArangoDB**.

---

## 🔹 Authentication & Security
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```
- Enforces **strong password policies**.
- Prevents **weak or common passwords**.

---

## 🔹 Localization & Timezone
```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```
- **Set language & timezone** for the application.
- **Use Internationalization (`USE_I18N`)** for translations.

---

## 🔹 Static Files (CSS, JavaScript, Images)
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```
- Defines the URL and **directory path for static files**.

---

## 🔹 Default Primary Key Type
```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```
- Defines the **default primary key type** for Django models.

---

## 🔹 Deployment Considerations
### **1️⃣ Disable Debug Mode in Production**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

### **2️⃣ Use Environment Variables for Security**
```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")
```

---

🎯 **Your Django settings are now fully documented!** 🚀

