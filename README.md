# Shririm - Gym Sessions Tracker

Shririm is a Django web application for tracking gym sessions, devices, and workout plans.

## Project Structure

```
shririm/
├── gym/                      # Main app directory
│   ├── migrations/           # Database migrations
│   ├── templates/            # HTML templates
│   │   └── gym/
│   │       ├── auth/         # Authentication templates
│   │       ├── devices/      # Device management templates
│   │       ├── plans/        # Workout plan templates
│   │       └── sessions/     # Gym session templates
│   ├── admin.py              # Admin site configuration
│   ├── forms.py              # Form definitions
│   ├── models.py             # Data models
│   ├── urls.py               # URL routing
│   └── views.py              # View functions
├── shririm/                  # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/                # Global templates
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Current Implementation

The application implements:

1. **User Authentication**: Login, logout, and registration
2. **Device Management**: Create, view, edit, and delete gym devices
3. **Workout Plans**: Create workout plans with ordered devices and settings
4. **Sessions**: Track gym sessions with device-specific settings and progress

## Models

- **Device**: Represents a gym equipment with name and description
- **Plan**: A workout plan containing multiple devices in a specific order
- **PlanDevice**: Joins Plan and Device with order and settings (weight, sets, etc.)
- **Session**: Represents a workout session using a specific plan
- **DeviceSession**: Represents a device used in a session with its settings and completion status

## Current Status

- All models, views, forms, and templates are implemented
- Database migrations have been created and applied
- Admin interface is configured
- Mobile-friendly UI with Bootstrap

## Tests

```
DJANGO_ENV=development python manage.py test
```

GitHub Actions runs them on every push to main and every pull request (`.github/workflows/tests.yml`).

## Next Steps

1. Fix the login URL issue
2. Add proper error handling
3. Implement user profile page
4. Add data visualization for tracking progress
5. Add search and filtering capabilities
6. Extend the test suite

## Configuration

Settings come from environment variables, or from a `.env` file next to `manage.py` (it is in `.gitignore`):

```
DJANGO_ENV=development      # Your own computer only: DEBUG on. Anything else (or unset) is production.
DJANGO_SECRET_KEY=...       # Required in production.
```

Make a secret key with
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.

## Setup for Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```
   python manage.py migrate
   ```

3. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```
   python manage.py runserver
   ```

5. Access the application at http://localhost:8000/

## Admin Access

- URL: http://localhost:8000/admin/, with the superuser you created.

## Technologies Used

- Django 4.2.23
- Bootstrap 5
- SQLite (development)