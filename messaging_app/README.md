# Multi-Container Setup for Messaging App

This project uses Docker Compose to manage a multi-container setup with a Django web application and a MySQL database.

## Requirements

- Docker
- Docker Compose

## Setup Instructions

1. Make sure you have Docker and Docker Compose installed on your system.

2. The project uses environment variables stored in a `.env` file. Ensure the `.env` file is present in the `messaging_app` directory with the following variables:

```
# Database settings
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=messaging_db
MYSQL_USER=messaging_user
MYSQL_PASSWORD=messaging_password

# Django settings
DEBUG=True
SECRET_KEY=django-insecure-9x!j&%d1q)9ga+6rs+e4&unr&9@zev^2k#zhcnx+u-l&m&x3ha
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Database connection for Django
DB_ENGINE=django.db.backends.mysql
DB_NAME=messaging_db
DB_USER=messaging_user
DB_PASSWORD=messaging_password
DB_HOST=db
DB_PORT=3306
```

Note: For security reasons, **do not commit** the `.env` file to version control.

## Running the Application

1. Build and start the containers:

```bash
docker-compose up --build
```

This will start both the web application and the MySQL database services.

2. To run in detached mode (background):

```bash
docker-compose up -d
```

3. To stop the containers:

```bash
docker-compose down
```

4. To stop and remove volumes:

```bash
docker-compose down -v
```

## Accessing the Application

- The Django web application will be available at: http://localhost:8000
- The MySQL database is available on port 3306

## Making Database Migrations

If you need to make migrations, you can run:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Creating a Superuser

To create a superuser for the Django admin interface:

```bash
docker-compose exec web python manage.py createsuperuser
```
