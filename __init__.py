"""Initialisation script for ShoppingList API"""
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

APP = FlaskAPI('__name__')
DB = SQLAlchemy(APP)
