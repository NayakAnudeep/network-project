# Integrating the Network Simulation App

This document provides instructions for integrating the Network Simulation app into the main AniTA web project.

## Step 1: Install Dependencies

Make sure all required packages are installed:

```bash
pip install networkx matplotlib numpy pandas python-louvain
```

## Step 2: Add the App to INSTALLED_APPS

In your `aniTA_web/settings.py` file, add the network_simulation app to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ... existing apps
    'network_simulation',
]
```

## Step 3: Configure URLs

In your main `aniTA_web/urls.py` file, include the network_simulation URLs:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing URL patterns
    path('network/', include('network_simulation.urls', namespace='network_simulation')),
]
```

## Step 4: Run Migrations

Create and apply migrations for the network_simulation models:

```bash
python manage.py makemigrations network_simulation
python manage.py migrate
```

## Step 5: Generate Sample Data

Generate sample data to populate the database:

```bash
# Create a directory for output files
mkdir -p network_simulation/csv_data

# Run the data generation script
python -c "from network_simulation.generate_data import generate_data; \
           from network_simulation.import_data import import_from_json; \
           data = generate_data(); \
           import json; \
           with open('network_data.json', 'w') as f: json.dump(data, f); \
           import_from_json('network_data.json')"
```

## Step 6: Add Navigation Links

Update your main application templates to include links to the network dashboard:

```html
<a href="{% url 'network_simulation:dashboard' %}">Network Analytics</a>
```

## Step 7: Static Files

Make sure your Django project is configured to serve static files properly:

```python
# In settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

## Troubleshooting

### Issue: Network visualizations not appearing
- Make sure matplotlib is properly installed
- Check that the `networkx` version is compatible (2.8.0 or higher recommended)

### Issue: Community detection not working
- Install the `python-louvain` package
- If unavailable, the system will fall back to connected components

### Issue: Performance issues with large datasets
- Reduce the data generation parameters in `generate_data.py`
- Add database indexes to frequently queried fields

## Integration with Existing User Authentication

If you want to integrate with your existing user authentication system:

1. Add the login_required decorator to views:
```python
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # ...
```

2. Update templates to use the authenticated user information:
```html
{% if user.is_authenticated %}
    <p>Welcome {{ user.username }}</p>
{% endif %}
```

## Customizing for Your Institution

1. Modify the `generate_data.py` script to use your institution's naming conventions
2. Update templates with your institution's branding
3. Adjust the data model if needed to match your educational structure
