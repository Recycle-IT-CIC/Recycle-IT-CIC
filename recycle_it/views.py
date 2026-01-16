from __future__ import annotations

from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func, or_

from . import db
from .models import Asset, Donor, Recipient, STATUS_CHOICES, STATUS_VALUES

bp = Blueprint("main", __name__)


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError("Please enter a valid number for weight.") from None


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - caught and surfaced to UI
        raise ValueError("Dates must be in YYYY-MM-DD format.") from exc


def _get_asset_or_404(asset_id: int) -> Asset:
    asset = db.session.get(Asset, asset_id)
    if asset is None:
        abort(404)
    return asset


@bp.route("/")
def dashboard():
    status_totals = {key: 0 for key, _ in STATUS_CHOICES}
    rows = (
        db.session.query(Asset.status, func.count(Asset.id))
        .group_by(Asset.status)
        .all()
    )
    for status, count in rows:
        status_totals[status] = count

    total_assets = sum(status_totals.values())
    total_weight = db.session.scalar(
        db.select(func.coalesce(func.sum(Asset.weight_kg), 0.0))
    ) or 0.0
    ready_for_distribution = status_totals.get("ready_for_distribution", 0)
    recycled = status_totals.get("recycled", 0) + status_totals.get("scrapped", 0)

    recent_assets = Asset.query.order_by(Asset.updated_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        status_totals=status_totals,
        total_assets=total_assets,
        total_weight=total_weight,
        ready_for_distribution=ready_for_distribution,
        recycled=recycled,
        recent_assets=recent_assets,
    )


@bp.route("/assets")
def asset_list():
    status = request.args.get("status")
    donor_id = request.args.get("donor")
    search = request.args.get("q")

    query = Asset.query

    if status:
        if status not in STATUS_VALUES:
            flash("Unknown status filter provided.", "warning")
            return redirect(url_for("main.asset_list"))
        query = query.filter(Asset.status == status)

    if donor_id:
        try:
            donor_id_int = int(donor_id)
        except ValueError:
            flash("Invalid donor filter provided.", "warning")
            return redirect(url_for("main.asset_list"))
        query = query.filter(Asset.donor_id == donor_id_int)

    if search:
        like_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Asset.tag.ilike(like_term),
                Asset.model.ilike(like_term),
                Asset.brand.ilike(like_term),
                Asset.serial_number.ilike(like_term),
            )
        )

    assets = query.order_by(Asset.updated_at.desc()).all()
    donors = Donor.query.order_by(Donor.name).all()

    return render_template(
        "assets/list.html",
        assets=assets,
        donors=donors,
        selected_status=status,
        selected_donor=donor_id,
        search=search or "",
    )


@bp.route("/assets/new", methods=["GET", "POST"])
def asset_create():
    donors = Donor.query.order_by(Donor.name).all()
    recipients = Recipient.query.order_by(Recipient.name).all()

    if request.method == "POST":
        form = request.form
        tag = form.get("tag", "").strip()
        asset_type = form.get("asset_type", "").strip()
        status = form.get("status", "collected")

        if not tag or not asset_type:
            flash("Tag and asset type are required.", "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=None,
                submit_label="Create asset",
                form_action=url_for("main.asset_create"),
            )

        if Asset.query.filter_by(tag=tag).first():
            flash("An asset with this tag already exists.", "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=None,
                submit_label="Create asset",
                form_action=url_for("main.asset_create"),
            )

        try:
            weight = _parse_float(form.get("weight_kg"))
            acquired_date = _parse_date(form.get("acquired_date"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=None,
                submit_label="Create asset",
                form_action=url_for("main.asset_create"),
            )

        if status not in STATUS_VALUES:
            flash("Invalid status selected.", "danger")
            status = "collected"

        asset = Asset(
            tag=tag,
            asset_type=asset_type,
            brand=form.get("brand"),
            model=form.get("model"),
            serial_number=form.get("serial_number"),
            condition=form.get("condition"),
            status=status,
            location=form.get("location"),
            weight_kg=weight,
            notes=form.get("notes"),
            acquired_date=acquired_date,
        )

        donor_id = form.get("donor_id")
        recipient_id = form.get("recipient_id")
        if donor_id:
            asset.donor_id = int(donor_id)
        if recipient_id:
            asset.recipient_id = int(recipient_id)

        db.session.add(asset)

        note = form.get("note") or "Asset created"
        recorded_by = form.get("recorded_by") or "system"
        try:
            asset.record_event(status, note=note, recorded_by=recorded_by)
        except ValueError:
            asset.record_event("collected", note=note, recorded_by=recorded_by)

        db.session.commit()
        flash("Asset created successfully.", "success")
        return redirect(url_for("main.asset_detail", asset_id=asset.id))

    return render_template(
        "assets/form.html",
        donors=donors,
        recipients=recipients,
        asset=None,
        submit_label="Create asset",
        form_action=url_for("main.asset_create"),
    )


@bp.route("/assets/<int:asset_id>")
def asset_detail(asset_id: int):
    asset = _get_asset_or_404(asset_id)
    donors = Donor.query.order_by(Donor.name).all()
    recipients = Recipient.query.order_by(Recipient.name).all()
    return render_template(
        "assets/detail.html",
        asset=asset,
        donors=donors,
        recipients=recipients,
    )


@bp.route("/assets/<int:asset_id>/edit", methods=["GET", "POST"])
def asset_edit(asset_id: int):
    asset = _get_asset_or_404(asset_id)
    donors = Donor.query.order_by(Donor.name).all()
    recipients = Recipient.query.order_by(Recipient.name).all()

    if request.method == "POST":
        form = request.form
        tag = form.get("tag", "").strip()
        asset_type = form.get("asset_type", "").strip()
        if not tag or not asset_type:
            flash("Tag and asset type are required.", "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=asset,
                submit_label="Save changes",
                form_action=url_for("main.asset_edit", asset_id=asset.id),
            )

        existing = Asset.query.filter_by(tag=tag).first()
        if existing and existing.id != asset.id:
            flash("Another asset already uses this tag.", "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=asset,
                submit_label="Save changes",
                form_action=url_for("main.asset_edit", asset_id=asset.id),
            )

        try:
            asset.weight_kg = _parse_float(form.get("weight_kg"))
            asset.acquired_date = _parse_date(form.get("acquired_date"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "assets/form.html",
                donors=donors,
                recipients=recipients,
                asset=asset,
                submit_label="Save changes",
                form_action=url_for("main.asset_edit", asset_id=asset.id),
            )

        asset.tag = tag
        asset.asset_type = asset_type
        asset.brand = form.get("brand")
        asset.model = form.get("model")
        asset.serial_number = form.get("serial_number")
        asset.condition = form.get("condition")
        asset.location = form.get("location")
        asset.notes = form.get("notes")

        donor_id = form.get("donor_id")
        recipient_id = form.get("recipient_id")
        asset.donor_id = int(donor_id) if donor_id else None
        asset.recipient_id = int(recipient_id) if recipient_id else None

        db.session.commit()
        flash("Asset updated successfully.", "success")
        return redirect(url_for("main.asset_detail", asset_id=asset.id))

    return render_template(
        "assets/form.html",
        donors=donors,
        recipients=recipients,
        asset=asset,
        submit_label="Save changes",
        form_action=url_for("main.asset_edit", asset_id=asset.id),
    )


@bp.route("/assets/<int:asset_id>/status", methods=["POST"])
def asset_update_status(asset_id: int):
    asset = _get_asset_or_404(asset_id)
    form = request.form
    status = form.get("status", asset.status)
    note = form.get("note") or None
    recorded_by = form.get("recorded_by") or None
    location = form.get("location") or None
    recipient_id = form.get("recipient_id") or None

    if status not in STATUS_VALUES:
        flash("Invalid status update.", "danger")
        return redirect(url_for("main.asset_detail", asset_id=asset.id))

    if recipient_id:
        asset.recipient_id = int(recipient_id)
    elif status not in {"donated", "ready_for_distribution"}:
        asset.recipient_id = None

    donor_id = form.get("donor_id")
    if donor_id:
        asset.donor_id = int(donor_id)

    asset.record_event(status, note=note, recorded_by=recorded_by, location=location)
    db.session.commit()
    flash("Asset status updated.", "success")
    return redirect(url_for("main.asset_detail", asset_id=asset.id))


@bp.route("/donors", methods=["GET", "POST"])
def donor_list():
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        if not name:
            flash("Name is required to add a donor.", "danger")
        else:
            donor = Donor(
                name=name,
                contact_name=form.get("contact_name"),
                email=form.get("email"),
                phone=form.get("phone"),
                notes=form.get("notes"),
            )
            db.session.add(donor)
            db.session.commit()
            flash("Donor added.", "success")
            return redirect(url_for("main.donor_list"))

    donors = Donor.query.order_by(Donor.name).all()
    return render_template("donors/list.html", donors=donors)


@bp.route("/recipients", methods=["GET", "POST"])
def recipient_list():
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        if not name:
            flash("Name is required to add a recipient organisation.", "danger")
        else:
            recipient = Recipient(
                name=name,
                contact_name=form.get("contact_name"),
                email=form.get("email"),
                phone=form.get("phone"),
                notes=form.get("notes"),
            )
            db.session.add(recipient)
            db.session.commit()
            flash("Recipient added.", "success")
            return redirect(url_for("main.recipient_list"))

    recipients = Recipient.query.order_by(Recipient.name).all()
    return render_template("recipients/list.html", recipients=recipients)
