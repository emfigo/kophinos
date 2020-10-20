from flask import Flask
import flask_login
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

from config import DATABASE_URI, KOPHINOS_API_SECRET

def unauthorized_handler():
    return 'unauthorized', HTTPStatus.UNAUTHORIZED

app = Flask(__name__)
app.secret_key = KOPHINOS_API_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

login_manager = flask_login.LoginManager()
login_manager.unauthorized_handler(unauthorized_handler)

login_manager.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
