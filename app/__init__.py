"""Initialisation script for ShoppingList API"""
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt

APP = FlaskAPI('__name__')
BCRPT = Bcrypt(APP)
DB = SQLAlchemy(APP)
DB.create_all()

BCRYPT_LOG_ROUNDS = 12
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/db_five'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
APP.config['SECRET_KEY'] = 'not_really_secret'
APP.config['WTF_CSRF_ENABLED'] = False

APP.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='david.mwebaza@andela.com',
    MAIL_PASSWORD='cr3{tW4ve',
))
MAIL = Mail(APP)
