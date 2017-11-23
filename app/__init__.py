"""Initialisation script for ShoppingList API"""
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

APP = FlaskAPI('__name__')
DB = SQLAlchemy(APP)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/db_five'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
APP.config['SECRET_KEY'] = 'not_really_secret'
APP.config['WTF_CSRF_ENABLED'] = False
