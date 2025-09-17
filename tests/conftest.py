import pytest

from recycle_it import create_app, db
from recycle_it.models import Donor, Recipient


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def donor_id(app):
    with app.app_context():
        donor = Donor(name="Test Donor")
        db.session.add(donor)
        db.session.commit()
        return donor.id


@pytest.fixture()
def recipient_id(app):
    with app.app_context():
        recipient = Recipient(name="Community Partner")
        db.session.add(recipient)
        db.session.commit()
        return recipient.id
