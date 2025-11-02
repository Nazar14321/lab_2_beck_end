from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

db.init_app(app)
migrate.init_app(app, db)

from . import models
from .views import bp
app.register_blueprint(bp)