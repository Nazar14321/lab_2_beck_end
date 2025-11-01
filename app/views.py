

from flask import request, jsonify
from . import app
from zoneinfo import ZoneInfo
from . import storage
from datetime import datetime

def err(message,status =400,**extra):
    return jsonify({"error":message,**extra}),status
def str_valid(s:object) -> str:
    if not isinstance(s, str):
        raise ValueError("must be a string")
    s = s.strip()
    if not s:
        raise ValueError("cannot be empty")
    if len(s) > 256:
        raise ValueError("too long (max 256)")
    return s

def int_valid(x)->int:
    if x is None:
        raise ValueError("not enough data")
    try:
        return int(x)
    except (TypeError, ValueError):
        raise ValueError("must be an integer")

def float_valid(x)->float:
    if x is None:
        raise ValueError("not enough data")
    try:
        return float(x)
    except (TypeError, ValueError):
        raise ValueError("must be a float")

def time_valid(x) -> str:
    if not isinstance(x, str):
        raise ValueError("datetime must be an ISO-8601 string")
    s = x.strip()
    if not s:
        raise ValueError("datetime cannot be empty")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("must be ISO-8601, e.g. 2025-11-01T12:34:56Z")
    return dt.isoformat()

@app.route("/")
def hello_world():
    return "<p>Hello, it's me amogus!</p>", 200

@app.get("/healthcheck")
def healthcheck():
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()
    }), 200

@app.get("/user/<int:user_id>")
def get_user(user_id:int):
    user=storage.user_data.get(user_id)
    if (user is None):
        return err("user not found",404)
    return jsonify({"id":user_id,"name":user}), 200

@app.get("/users")
def get_users():
    return jsonify([{"id": i, "name": name} for i, name in storage.user_data.items()]), 200

@app.post("/user")
def add_user():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    cat_data=request.get_json() or {}
    try:
        name = str_valid(cat_data.get("name"))
    except ValueError as e:
        return err(f"not enough user data: {e}", 400)
    user_id=max(storage.user_data.keys() or [0]) + 1
    storage.user_data[user_id]=name
    return jsonify({"id":user_id, "name":name}), 201

@app.delete("/user/<int:user_id>")
def kill_user(user_id:int):
    name = storage.user_data.pop(user_id, None)
    if (name is None):
        return err("user not found",404)
    return jsonify({"result":f"id: {user_id} successfully deleted","name":name}),200

@app.get("/category")
def get_categories():
    return jsonify([{"id":i, "name":name} for i,name in storage.category_data.items()]),200

@app.post("/category")
def add_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    cat_data=request.get_json() or {}
    try:
        name = str_valid(cat_data.get("name"))
    except ValueError as e:
        return err(f"not enough category data: {e}", 400)
    category_id=max(storage.category_data.keys() or [0]) + 1
    storage.category_data[category_id]=name
    return jsonify({"id":category_id, "name":name}), 201

@app.delete("/category")
def kill_category():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    cat_data=request.get_json() or {}
    try:
        cid=int_valid(cat_data.get("id"))
    except ValueError as e:
        return err(str(e), 400)
    name= storage.category_data.pop(cid,None)
    if name is None:
        return err("category not found",404)
    return jsonify({"result": f"id: {cid} successfully deleted", "name": name}), 200

@app.get("/record/<int:record_id>")
def get_record(record_id:int):
    record=storage.records_data.get(record_id)
    if (record is None):
        return err("record not found",404)
    return jsonify({"id":record_id,"user_id":record["user_id"],"category_id":record["category_id"],"datetime":record["datetime"],"amount":record["amount"]}), 200


@app.delete("/record/<int:record_id>")
def kill_record(record_id:int):
    record = storage.records_data.pop(record_id, None)
    if (record is None):
        return err("record not found",404)
    return jsonify({"result":f"id: {record_id} successfully deleted","deleted": {"id": record_id, **record}}),200

@app.post("/record")
def add_record_data():
    if not request.is_json:
        return err("Content-Type must be application/json", 415)
    cat_data=request.get_json() or {}
    try :
        user_id=int_valid(cat_data.get("user_id"))
        category_id=int_valid(cat_data.get("category_id"))
    except ValueError as e:
        return err(str(e), 400)
    try :
        amount=float_valid(cat_data.get("amount"))
    except ValueError as e:
        return err(str(e), 400)
    try:
        date_time=time_valid(cat_data.get("datetime"))
    except ValueError as e:
        return err(str(e), 400)
    if user_id not in storage.user_data:
        return err(f"user_id {user_id} not found", 404)
    if category_id not in storage.category_data:
        return err(f"category_id {category_id} not found", 404)

    record_id=max(storage.records_data.keys() or [0]) + 1
    input_data={"user_id":user_id,"category_id":category_id,"datetime":date_time,"amount":amount}
    storage.records_data[record_id]=input_data
    return jsonify({"id": record_id, **input_data}), 201

@app.get("/record")
def find_record_data():
    uid = request.args.get("user_id", type=int)
    cid = request.args.get("category_id", type=int)
    if uid is None and cid is None:
        return err("provide user_id and/or category_id")

    items = [
        {"id": i, **rec}
        for i, rec in storage.records_data.items()
        if (uid is None or rec["user_id"] == uid)
        and (cid is None or rec["category_id"] == cid)
    ]
    return jsonify({"items": items, "count": len(items)}), 200


