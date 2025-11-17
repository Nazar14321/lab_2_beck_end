from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from zoneinfo import ZoneInfo
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required

from . import db, schemas
from .models import User, Category, Record

bp = Blueprint("api", __name__)

user_schema            = schemas.User_Schema()
users_schema           = schemas.User_Schema(many=True)
category_schema        = schemas.Category_Schema()
categories_schema      = schemas.Category_Schema(many=True)
record_schema          = schemas.Record_Schema()
records_schema         = schemas.Record_Schema(many=True)

category_delete_schema = schemas.CategoryDeleteSchema()
category_query_schema  = schemas.CategoryQuerySchema()
record_query_schema    = schemas.RecordQuerySchema()
user_id_path_schema    = schemas.UserIdPathSchema()
record_id_path_schema  = schemas.RecordIdPathSchema()

user_register_schema   = schemas.UserRegisterSchema()
user_login_schema      = schemas.UserLoginSchema()


def err(message, status=400, **extra):
    return jsonify({"error": message, **extra}), status


@bp.route("/")
def hello_world():
    return "<p>Hello, it's me amogus!</p>", 200


@bp.get("/healthcheck")
def healthcheck():
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()
    }), 200


@bp.post("/user")
def register_user():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = user_register_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid user data", 400, details=e.messages)

    if User.query.filter_by(name=data["name"]).first():
        return err("user with this name already exists", 409)

    user = User(name=data["name"], password=pbkdf2_sha256.hash(data["password"]))
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name}), 201


@bp.post("/login")
def login():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = user_login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid login data", 400, details=e.messages)

    user = User.query.filter_by(name=data["name"]).first()
    if not user or not pbkdf2_sha256.verify(data["password"], user.password):
        return err("invalid credentials", 401)

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200


@bp.get("/user/<int:user_id>")
@jwt_required()
def get_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return err("user not found", 404)
    return jsonify(user_schema.dump({"id": user_id, "name": user.name})), 200


@bp.get("/users")
@jwt_required()
def get_users():
    users = User.query.order_by(User.id.asc()).all()
    items = [{"id": u.id, "name": u.name} for u in users]
    return jsonify(users_schema.dump(items)), 200


@bp.delete("/user/<int:user_id>")
@jwt_required()
def kill_user(user_id: int):
    try:
        args = user_id_path_schema.load({"user_id": user_id})
    except ValidationError as e:
        return err("invalid path parameter", 400, details=e.messages)

    user = User.query.get(args["user_id"])
    if user is None:
        return err("user not found", 404)

    name = user.name
    db.session.delete(user)
    db.session.commit()
    return jsonify({"result": f"id: {user_id} successfully deleted", "name": name}), 200


@bp.get("/category")
@jwt_required()
def get_categories():
    try:
        args = category_query_schema.load(request.args)
    except ValidationError as e:
        return err("invalid query", 400, details=e.messages)

    uid = args.get("user_id")
    if uid is None:
        q = Category.query.filter(Category.owner_id.is_(None))
    else:
        q = Category.query.filter(
            or_(Category.owner_id.is_(None), Category.owner_id == uid)
        )

    categories = q.order_by(Category.owner_id.isnot(None), Category.name.asc()).all()
    items = [{"id": c.id, "name": c.name, "owner_id": c.owner_id} for c in categories]
    return jsonify(categories_schema.dump(items)), 200


@bp.post("/category")
@jwt_required()
def add_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        data = category_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid category data", 400, details=e.messages)

    owner_id = data.get("user_id")
    if owner_id is not None and User.query.get(owner_id) is None:
        return err(f"user_id {owner_id} not found", 404)

    category = Category(name=data["name"], owner_id=owner_id)
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return err("category with this name already exists in scope", 409)

    return jsonify(category_schema.dump({
        "id": category.id,
        "name": category.name,
        "owner_id": owner_id
    })), 201


@bp.delete("/category")
@jwt_required()
def kill_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    try:
        payload = category_delete_schema.load(request.get_json() or {})
    except ValidationError as e:
        return err("invalid category data", 400, details=e.messages)

    cid = payload["id"]
    uid = payload.get("user_id")

    category = Category.query.get(cid)
    if category is None:
        return err("category not found", 404)

    if uid is None:
        if category.owner_id is None:
            name = category.name
            db.session.delete(category)
            db.session.commit()
            return jsonify({"result": f"id: {cid} successfully deleted", "name": name}), 200
        return err("user_id is required to delete personal category", 400)

    if category.owner_id is None:
        return err("to delete a global category omit user_id in request body", 403)

    if uid != category.owner_id:
        return err("cannot delete category that does not belong to the user", 403)

    name = category.name
    db.session.delete(category)
    db.session.commit()
    return jsonify({"result": f"id: {cid} successfully deleted", "name": name}), 200


@bp.get("/record/<int:record_id>")
@jwt_required()
def get_record(record_id: int):
    record = Record.query.get(record_id)
    if record is None:
        return err("record not found", 404)

    return jsonify(record_schema.dump({
        "id": record.id,
        "user_id": record.user_id,
        "category_id": record.category_id,
        "datetime": record.datetime,
        "amount": record.amount,
    })), 200


@bp.post("/record")
@jwt_required()
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

    category = Category.query.get(category_id)
    if category is None:
        return err(f"category_id {category_id} not found", 404)

    if not (category.owner_id is None or category.owner_id == user_id):
        return err("category is not visible for this user", 400)

    record = Record(
        user_id=user_id,
        category_id=category_id,
        datetime=data["datetime"],
        amount=data["amount"],
    )
    db.session.add(record)
    db.session.commit()

    return jsonify(record_schema.dump({
        "id": record.id,
        "user_id": user_id,
        "category_id": category_id,
        "datetime": record.datetime,
        "amount": record.amount,
    })), 201


@bp.delete("/record/<int:record_id>")
@jwt_required()
def kill_record(record_id: int):
    try:
        args = record_id_path_schema.load({"record_id": record_id})
    except ValidationError as e:
        return err("invalid path parameter", 400, details=e.messages)

    record = Record.query.get(args["record_id"])
    if record is None:
        return err("record not found", 404)

    rec = {
        "user_id": record.user_id,
        "category_id": record.category_id,
        "datetime": record.datetime,
        "amount": record.amount,
    }

    db.session.delete(record)
    db.session.commit()

    return jsonify({
        "result": f"id: {record_id} successfully deleted",
        "deleted": record_schema.dump({"id": record_id, **rec})
    }), 200


@bp.get("/record")
@jwt_required()
def find_record_data():
    try:
        args = record_query_schema.load(request.args)
    except ValidationError as e:
        return err("invalid query", 400, details=e.messages)

    uid = args.get("user_id")
    cid = args.get("category_id")

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
        "datetime": r.datetime,
        "amount": r.amount,
    } for r in rows]

    return jsonify({"items": records_schema.dump(items), "count": len(items)}), 200
