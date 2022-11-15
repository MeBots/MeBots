import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'views.login'

from app import views, models, errors, api, util, groupme_api
app.register_blueprint(views.views_blueprint)
app.register_blueprint(api.api_blueprint, url_prefix='/api')
