from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from zoneinfo import ZoneInfo
from datetime import datetime

from . import db
from . import schemas
from .models import User, Category, Record

bp = Blueprint("api", __name__)

user_schema       = schemas.User_Schema()
users_schema      = schemas.User_Schema(many=True)
category_schema   = schemas.Category_Schema()
categories_schema = schemas.Category_Schema(many=True)
record_schema     = schemas.Record_Schema()
records_schema    = schemas.Record_Schema(many=True)

def err(message, status=400, **extra):
    return jsonify({"error": message, **extra}), status

@bp.route("/")
def hello_world():
    return "<p>Hello, it's me amogus!</p>", 200

@bp.get("/healthcheck")
def healthcheck():
    return jsonify({"status": "OK", "timestamp": datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()}), 200

@bp.get("/user/<int:user_id>")
def get_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return err("user not found", 404)
    return jsonify(user_schema.dump({"id": user_id, "name": user.name})), 200

@bp.get("/users")
def get_users():
    users = User.query.order_by(User.id.asc()).all()
    items = [{"id": u.id, "name": u.name} for u in users]
    return jsonify(users_schema.dump(items)), 200

@bp.post("/user")
def add_user():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = user_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid user data", 400, details=e.messages)
    user = User(name=data["name"])
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    return jsonify(user_schema.dump({"id": user_id, **data})), 201

@bp.delete("/user/<int:user_id>")
def kill_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return err("user not found", 404)
    name = user.name
    db.session.delete(user)
    db.session.commit()
    return jsonify({"result": f"id: {user_id} successfully deleted", "name": name}), 200

@bp.get("/category")
def get_categories():
    categories = Category.query.order_by(Category.id.asc()).all()
    items = [{"id": c.id, "name": c.name} for c in categories]
    return jsonify(categories_schema.dump(items)), 200

@bp.post("/category")
def add_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = category_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid category data", 400, details=e.messages)
    category = Category(name=data["name"])
    db.session.add(category)
    db.session.commit()
    category_id = category.id
    return jsonify(category_schema.dump({"id": category_id, **data})), 201

@bp.delete("/category")
def kill_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    payload = request.get_json() or {}
    try:
        cid = int(payload.get("id"))
    except (TypeError, ValueError):
        return err("id must be an integer", 400)
    category = Category.query.get(cid)
    if category is None:
        return err("category not found", 404)
    name = category.name
    db.session.delete(category)
    db.session.commit()
    return jsonify({"result": f"id: {cid} successfully deleted", "name": name}), 200

@bp.get("/record/<int:record_id>")
def get_record(record_id: int):
    record = Record.query.get(record_id)
    if record is None:
        return err("record not found", 404)
    return jsonify(record_schema.dump({
        "id": record.id,
        "user_id": record.user_id,
        "category_id": record.category_id,
        "datetime": record.datetime.isoformat(),
        "amount": record.amount,
    })), 200

@bp.post("/record")
def add_record_data():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = record_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid record data", 400, details=e.messages)
    user_id = data["user_id"]
    category_id = data["category_id"]
    if User.query.get(user_id) is None:
        return err(f"user_id {user_id} not found", 404)
    if Category.query.get(category_id) is None:
        return err(f"category_id {category_id} not found", 404)
    record = Record(
        user_id=user_id,
        category_id=category_id,
        datetime=data["datetime"],
        amount=float(data["amount"]),
    )
    db.session.add(record)
    db.session.commit()
    record_id = record.id
    payload = {
        "user_id": user_id,
        "category_id": category_id,
        "datetime": record.datetime.isoformat(),
        "amount": record.amount,
    }
    return jsonify(record_schema.dump({"id": record_id, **payload})), 201

@bp.delete("/record/<int:record_id>")
def kill_record(record_id: int):
    record = Record.query.get(record_id)
    if record is None:
        return err("record not found", 404)
    rec = {
        "user_id": record.user_id,
        "category_id": record.category_id,
        "datetime": record.datetime.isoformat(),
        "amount": record.amount,
    }
    db.session.delete(record)
    db.session.commit()
    return jsonify({"result": f"id: {record_id} successfully deleted",
                    "deleted": record_schema.dump({"id": record_id, **rec})}), 200

@bp.get("/record")
def find_record_data():
    uid = request.args.get("user_id", type=int)
    cid = request.args.get("category_id", type=int)
    if uid is None and cid is None:
        return err("provide user_id and/or category_id")
    q = Record.query
    if uid is not None:
        q = q.filter_by(user_id=uid)
    if cid is not None:
        q = q.filter_by(category_id=cid)
    rows = q.order_by(Record.id.asc()).all()
    items = [{
        "id": r.id,
        "user_id": r.user_id,
        "category_id": r.category_id,
        "datetime": r.datetime.isoformat(),
        "amount": r.amount,
    } for r in rows]
    return jsonify({"items": records_schema.dump(items), "count": len(items)}), 200
