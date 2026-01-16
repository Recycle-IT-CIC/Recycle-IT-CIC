import os

import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance shared across modules
db = SQLAlchemy()


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the Recycle IT asset management system."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "recycle_it.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    # Ensure instance folder exists for SQLite database when not testing
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    from . import models  # noqa: WPS433 (import after initializing db)
    from .views import bp as views_bp

    app.register_blueprint(views_bp)

    @app.context_processor
    def inject_template_helpers():
        """Expose status labels to templates."""
        return {
            "STATUS_CHOICES": models.STATUS_CHOICES,
            "STATUS_LABELS": dict(models.STATUS_CHOICES),
        }

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables."""
        with app.app_context():
            db.create_all()
        click.echo("Initialized the database.")

    @app.cli.command("seed-data")
    def seed_data_command():
        """Populate the database with seed records for demo purposes."""
        from .models import Asset, Donor, Recipient

        with app.app_context():
            if Donor.query.count() > 0 or Asset.query.count() > 0:
                click.echo("Database already contains data; skipping seed.")
                return

            donors = [
                Donor(name="Community Library", contact_name="Jamie Perez", email="library@example.org", phone="555-1023"),
                Donor(name="Tech Hub Ltd", contact_name="Priya Singh", email="it@techhub.example", phone="555-3344"),
            ]
            recipients = [
                Recipient(name="Digital Inclusion Centre", contact_name="Reece Thompson", email="reece@dic.org"),
                Recipient(name="Green Future School", contact_name="Alex Rivers", email="arivers@greenfuture.edu"),
            ]

            db.session.add_all(donors + recipients)
            db.session.flush()

            assets = [
                Asset(
                    tag="LAP-001",
                    asset_type="Laptop",
                    brand="Dell",
                    model="Latitude 5400",
                    serial_number="DL12345",
                    condition="Used - Good",
                    status="ready_for_distribution",
                    location="Warehouse A",
                    weight_kg=2.1,
                    donor=donors[0],
                    notes="Clean install completed",
                ),
                Asset(
                    tag="MON-010",
                    asset_type="Monitor",
                    brand="HP",
                    model="Z24n",
                    serial_number="HP98765",
                    condition="Used - Fair",
                    status="in_refurbishment",
                    location="Tech Bench",
                    weight_kg=5.5,
                    donor=donors[1],
                    notes="Needs new power cable",
                ),
                Asset(
                    tag="DES-104",
                    asset_type="Desktop",
                    brand="Lenovo",
                    model="ThinkCentre M720",
                    serial_number="LN24680",
                    condition="Used - Good",
                    status="collected",
                    location="Pickup Van",
                    weight_kg=7.2,
                    donor=donors[1],
                    notes="Awaiting assessment",
                ),
            ]

            for asset in assets:
                db.session.add(asset)
                asset.record_event(asset.status, note="Seed data import", recorded_by="system")

            db.session.commit()
        click.echo("Seed data created.")

    return app


# Provide a default Flask app for WSGI servers
app = create_app()

__all__ = ["create_app", "db", "app"]
