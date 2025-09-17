from recycle_it import db
from recycle_it.models import Asset, Donor


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_asset_creation_flow(client, app, donor_id):
    response = client.post(
        "/assets/new",
        data={
            "tag": "A-100",
            "asset_type": "Desktop",
            "brand": "Dell",
            "model": "Optiplex",
            "serial_number": "SN123",
            "condition": "Used - Good",
            "status": "collected",
            "donor_id": str(donor_id),
            "note": "Picked up from donor",
            "recorded_by": "Jess",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Asset created successfully" in response.data

    with app.app_context():
        asset = db.session.scalar(db.select(Asset).filter_by(tag="A-100"))
        assert asset.donor_id == donor_id
        assert asset.logs[0].recorded_by == "Jess"


def test_asset_status_update(client, app, donor_id):
    with app.app_context():
        donor = db.session.get(Donor, donor_id)
        asset = Asset(tag="A-200", asset_type="Laptop", donor=donor)
        db.session.add(asset)
        db.session.commit()
        asset_id = asset.id

    response = client.post(
        f"/assets/{asset_id}/status",
        data={
            "status": "in_refurbishment",
            "note": "Wiped and ready for QA",
            "recorded_by": "Kai",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Asset status updated" in response.data

    with app.app_context():
        asset = db.session.get(Asset, asset_id)
        assert asset.status == "in_refurbishment"
        assert asset.logs[0].note == "Wiped and ready for QA"
