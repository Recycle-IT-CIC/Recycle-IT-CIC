from __future__ import annotations

from datetime import datetime

from sqlalchemy import func

from . import db

STATUS_CHOICES = (
    ("collected", "Collected"),
    ("in_assessment", "In assessment"),
    ("in_refurbishment", "In refurbishment"),
    ("ready_for_distribution", "Ready for distribution"),
    ("donated", "Donated"),
    ("recycled", "Recycled"),
    ("scrapped", "Scrapped"),
)

STATUS_VALUES = {choice for choice, _ in STATUS_CHOICES}


class TimestampMixin:
    """Mixin that adds created/updated timestamps."""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Donor(TimestampMixin, db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)

    assets = db.relationship("Asset", back_populates="donor", lazy="dynamic")

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging
        return f"<Donor {self.name!r}>"


class Recipient(TimestampMixin, db.Model):
    __tablename__ = "recipients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)

    assets = db.relationship("Asset", back_populates="recipient", lazy="dynamic")

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging
        return f"<Recipient {self.name!r}>"


class Asset(TimestampMixin, db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), unique=True, nullable=False)
    asset_type = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(120))
    model = db.Column(db.String(120))
    serial_number = db.Column(db.String(120))
    condition = db.Column(db.String(120))
    status = db.Column(db.String(50), nullable=False, default="collected")
    location = db.Column(db.String(255))
    acquired_date = db.Column(db.Date)
    weight_kg = db.Column(db.Float)
    notes = db.Column(db.Text)

    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipients.id"))

    donor = db.relationship("Donor", back_populates="assets")
    recipient = db.relationship("Recipient", back_populates="assets")

    logs = db.relationship(
        "AssetLog",
        back_populates="asset",
        order_by=lambda: AssetLog.recorded_at.desc(),
        cascade="all, delete-orphan",
    )

    def record_event(
        self,
        status: str,
        note: str | None = None,
        recorded_by: str | None = None,
        location: str | None = None,
    ) -> "AssetLog":
        """Update the asset status and create an audit log entry."""
        if status not in STATUS_VALUES:
            raise ValueError(f"Unknown status '{status}'.")
        if location is not None:
            self.location = location
        self.status = status
        self.updated_at = datetime.utcnow()
        event = AssetLog(status=status, note=note, recorded_by=recorded_by)
        self.logs.append(event)
        return event

    @property
    def status_label(self) -> str:
        """Return the human readable label for the current status."""
        return dict(STATUS_CHOICES).get(self.status, self.status)

    @staticmethod
    def total_weight() -> float:
        """Return the total weight of all assets."""
        return db.session.scalar(db.select(func.coalesce(func.sum(Asset.weight_kg), 0.0))) or 0.0

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging
        return f"<Asset {self.tag!r} {self.status!r}>"


class AssetLog(TimestampMixin, db.Model):
    __tablename__ = "asset_logs"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Text)
    recorded_by = db.Column(db.String(120))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False)
    asset = db.relationship("Asset", back_populates="logs")

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging
        return f"<AssetLog asset={self.asset_id} status={self.status!r}>"
