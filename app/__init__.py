"""Initialisation script for ShoppingList API
"""

from flask_api import FlaskAPI
from config import Config
# from flasgger import Swagger
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy


app = FlaskAPI('__name__')
app.config.from_object(Config)
bcrypt = Bcrypt(app)
CORS(app)
db = SQLAlchemy(app)
login_mgr = LoginManager()
login_mgr.init_app(app)
login_mgr.login_view = 'login'
mail = Mail(app)
migr = Migrate(app, db)
mgr = Manager(app)

from app import models
from app.views import auth_views, list_views, item_views
