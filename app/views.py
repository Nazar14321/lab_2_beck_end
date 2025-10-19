from flask import request, jsonify
from . import app
from . import storage
@app.route("/")
def hello_world():
    return "<p>Hello, it's me amogus!</p>"

@app.get("/health")
def health_check():
    return{"status":"ok"}

@app.get("/user/<int:user_id>")
def get_user(user_id:int):
    user=storage.user_data.get(user_id)
    if (user is None):
        return {"error": "user not found"}, 404
    return {"id":user_id,"name":user}, 200

@app.get("/users")
def get_users():
    return [{"id": i, "name": name} for i, name in storage.user_data.items()], 200

@app.post("/user")
def add_user():
    cat_data=request.get_json()
    if (not cat_data or "name" not in cat_data ):
        return {"error": " not enough user data"},400
    user_id=max(storage.user_data.keys() or [0]) + 1
    storage.user_data[user_id]=cat_data["name"]
    return {"id":user_id, "name":cat_data["name"]}, 201

@app.delete("/user/<int:user_id>")
def kill_user(user_id:int):
    if not(user_id in storage.user_data):
        return {"error": "user not found"}, 404
    name= storage.user_data.pop(user_id,None)
    return{"result":f"id: {user_id} successful deleted","name":name},200

@app.get("/category")
def get_categories():
    return [{"id":i, "name":name} for i,name in storage.category_data.items()],200

@app.post("/category")
def add_category():
    cat_data=request.get_json()
    if (not cat_data or "name" not in cat_data ):
        return {"error": " not enough user data"},400
    record_id=max(storage.category_data.keys() or [0]) + 1
    storage.category_data[record_id]=cat_data["name"]
    return {"id":record_id, "name":cat_data["name"]}, 201

@app.delete("/category")
def kill_category():
    cat_data=request.get_json()
    if (not cat_data or "id" not in cat_data):
        return {"error": " incorrect id to delete category_data"},400
    category_id= int(cat_data["id"])
    name= storage.category_data.pop(category_id,None)
    if name is None:
        return {"error": "category not found"}, 404
    return {"result": f"id: {category_id} successful deleted", "name": name}, 200


