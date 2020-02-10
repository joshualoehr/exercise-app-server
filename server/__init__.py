import os
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app_settings = os.getenv(
    'APP_SETTINGS',
    'server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from server.routes import *  # noqa: E402
