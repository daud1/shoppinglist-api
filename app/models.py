"""Database models for User, List and Item tables
"""
import datetime
import math

import jwt
from flask_login import UserMixin, current_user
from itsdangerous import BadSignature, Serializer, SignatureExpired
from sqlalchemy import func

from ..app import app, bcrypt, db


class User(db.Model, UserMixin):
    """This class represents the user table
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    token = db.Column(db.Text(), nullable=True)
    lists = db.relationship('ShoppingList', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config['BCRYPT_LOG_ROUNDS']).decode()

    def __repr__(self):
        return '<Email %r>' % self.email

    @property
    def serialize(self):
        """Return object data in easily serializeable format
        """
        return {'email': self.email, 'password': self.password}

    def encode_auth_token(self):
        """Encodes a jwt auth token
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow()\
                        + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            return jwt.encode(
                payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        '''Decodes the auth token
        '''
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class ShoppingList(db.Model):
    """This class represents the shopping_list table
    """
    __tablename__ = 'shopping_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format
        """
        return {'name': self.name, 'list_id': self.id, 'user_id': self.user_id}

    @staticmethod
    def search(que, id, page=1):
        """This method searches for a list and returns paginated results.
        """
        all_lists = ShoppingList.query.filter_by(user_id=id)
        count = all_lists.count()
        limit = 7

        if que:
            all_lists = all_lists.filter(
                func.lower(
                    ShoppingList.name).like("%" + que.lower().strip() + "%"))
            count = all_lists.count()
            
        return {
            'lists': all_lists.paginate(page, limit).items,
            'number_of_pages': math.ceil(count / limit)
        }


class Item(db.Model):
    """This class represents the item table
    """
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    list_id = db.Column(
        db.Integer,
        db.ForeignKey('shopping_list.id', ondelete='CASCADE'),
        nullable=False)

    def __init__(self, name, list_id):
        self.name = name
        self.list_id = list_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format
        """
        return {
            'item_id': self.item_id,
            'name': self.name,
            'list_id': self.list_id
        }

    @staticmethod
    def search(que, id, page=1):
        """This method implements search and pagination.
        """
        all_items = Item.query.filter_by(list_id=id)
        count = all_items.count()
        limit = 7

        if que:
            all_items = all_items.filter(
                func.lower(Item.name).like("%" + que.lower().strip() + "%"))
            count = all_items.count()

        return {
            'items': all_items.paginate(page, limit).items,
            'number_of_pages': math.ceil(count / limit)
        }
