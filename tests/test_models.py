from recycle_it import db
from recycle_it.models import Asset, Donor, STATUS_CHOICES, STATUS_VALUES


def test_asset_record_event_updates_status(app):
    with app.app_context():
        donor = Donor(name="Library")
        asset = Asset(tag="A-001", asset_type="Laptop", donor=donor)
        db.session.add_all([donor, asset])
        db.session.commit()

        asset.record_event("in_refurbishment", note="Diagnostics complete", recorded_by="Technician")
        asset.record_event("ready_for_distribution", note="Imaged and bagged", recorded_by="Technician")
        db.session.commit()

        assert asset.status == "ready_for_distribution"
        assert asset.logs[0].note == "Imaged and bagged"
        assert asset.logs[0].recorded_by == "Technician"
        assert asset.logs[0].status == "ready_for_distribution"


def test_status_choices_cover_values():
    labels = dict(STATUS_CHOICES)
    for value in STATUS_VALUES:
        assert value in labels
