import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401


@jwt.unauthorized_loader
def missing_token(error):
    return jsonify(
        {
            "description": "Request does not contain an access token.",
            "error": "authorization_required",
        }
    ), 401


app = Flask(__name__)

app.config.from_pyfile("config.py", silent=True)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

db.init_app(app)
jwt.init_app(app)

migrate.init_app(app, db)

from . import models
from .views import bp

app.register_blueprint(bp)


@app.cli.command("seed")
def seed_command():
    from .seed import run_seed

    run_seed(reset=True)
