
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
    return user, 200

@app.get("/users")
def get_users():
    return [{"id":i, "name":name} for i,name in storage.user_data.values()],200

