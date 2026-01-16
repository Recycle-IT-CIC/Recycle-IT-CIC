# Recycle IT Asset Management System

A lightweight, self-hosted web application to help e-waste social enterprises capture, track and report on donated computer equipment. Built with [Flask](https://flask.palletsprojects.com/) and SQLite so it can run on modest hardware or a cloud VM without external dependencies.

## Features

- **Asset lifecycle tracking** – record each device collected, monitor refurbishment stages and log when items are donated or recycled.
- **Donor and recipient directory** – store contact details for organisations who give or receive equipment.
- **Operational dashboard** – visualise pipeline totals, recent activity and the combined weight of equipment processed.
- **Activity history** – maintain an audit trail of every status update with notes and staff attribution.
- **Seed data** – bootstrap the system with sample donors, recipients and assets for demos or testing.

## Getting started

### 1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialise the database

```bash
flask --app recycle_it:create_app init-db
flask --app recycle_it:create_app seed-data  # optional demo records
```

Both commands create a SQLite database in the `instance/` directory (automatically created on first run).

### 3. Run the development server

```bash
flask --app recycle_it:create_app --debug run
```

The application will be available at http://127.0.0.1:5000. Use the navigation to create donors/recipients, log new assets and update their status as they progress through refurbishment.

## Running the tests

```bash
pytest
```

## Project structure

```
recycle_it/           # Flask app package
├── __init__.py       # Application factory and CLI commands
├── models.py         # SQLAlchemy models and status helpers
└── views.py          # Routes, business logic and validation
static/css/           # Styling
templates/            # Jinja templates for dashboard, assets and directories
tests/                # Pytest test suite
```

## Deployment notes

- Flask configuration values such as `SECRET_KEY` and database URI can be overridden via environment variables when deploying to production.
- Back up the `instance/recycle_it.db` SQLite file regularly, or switch to another SQLAlchemy-supported database by updating `SQLALCHEMY_DATABASE_URI`.
- Consider placing the application behind a production-ready web server (e.g. Gunicorn + Nginx) for secure public access.
