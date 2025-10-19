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
    return [{"id":i, "name":name} for i,name in storage.user_data.values()],200

@app.post("/user")
def add_user():
    user_data=request.get_json()
    if (not user_data or "name" not in user_data ):
        return {"error": " not enough user data"},400
    user_id=max(storage.user_data.keys() or [0]) + 1
    storage.user_data[user_id]=user_data["name"]
    return {"id":user_id, "name":user_data["name"]}, 201

@app.delete("/user/<int:user_id>")
def kill_user(user_id:int):
    if not(user_id in storage.user_data):
        return {"error": "user not found"}, 404
    name= storage.user_data.pop(user_id,None)
    return{"result":f"id: {user_id} successful deleted","name":name},200

