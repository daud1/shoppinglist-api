"""Database models for User, List and Item tables"""
import math

from flask_login import UserMixin, current_user
from itsdangerous import Serializer, SignatureExpired, BadSignature
from sqlalchemy import func

from app import app, bcrypt, db

class User(db.Model, UserMixin):
    """This class represents the user table"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    token = db.Column(db.String(255), nullable=True)
    lists = db.relationship('ShoppingList', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config['BCRYPT_LOG_ROUNDS']).decode()

    def generate_auth_token(self, expiration=10800):
        """method to generate an authorisation token for user on successful login"""
        ser = Serializer(app.config['SECRET_KEY'])
        return ser.dumps({'id': self.id})

    def __repr__(self):
        return '<Email %r>' % self.email

    @staticmethod
    def verify_auth_token(token):
        """method to verify authorisation token"""
        ser = Serializer(app.config['SECRET_KEY'])
        try:
            data = ser.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'email': self.email, 'password': self.password}


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
        return {
            'name': self.name,
            'list_id': self.id,
            'user_id': self.user_id
        }

    @staticmethod
    def search(que, page=1):
        """This method implements search and pagination.
        """
        all_lists = ShoppingList.query.filter_by(user_id=current_user.id)
        count = all_lists.count()
        limit = 10

        if que:
            all_lists = all_lists.filter(
                func.lower(ShoppingList.name).like(
                    "%" + que.lower().strip() + "%")
            )
            count = all_lists.count()

        if isinstance(page, int):
            return {'lists': all_lists.paginate(page, limit, False).items,
                    'number_of_pages': math.ceil(count / limit)}
        return {'lists': all_lists.all(), 'number_of_pages': math.ceil(count / limit)}


class Item(db.Model):
    """This class represents the item table
    """
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    quantity = db.Column(db.Integer)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'shopping_list.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, name, list_id, quantity=1):
        self.name = name
        self.list_id = list_id
        self.quantity = quantity

    @property
    def serialize(self):
        """Return object data in easily serializeable format
        """
        return {
            'item_id': self.item_id,
            'name': self.name,
            'quantity': self.quantity,
            'list_id': self.list_id
        }

    @staticmethod
    def search(que, id, page=1):
        """This method implements search and pagination.
        """
        all_items = Item.query.filter_by(list_id=id)
        count = all_items.count()
        limit = 10
        if que:
            all_items = all_items.filter(
                func.lower(Item.name).like(
                    "%" + que.lower().strip() + "%")
            )
            count = all_items.count()
        if isinstance(page, int):
            return {'items': all_items.paginate(page, limit, False).items,
                    'number_of_pages': math.ceil(count / limit)}
        return {'items': all_items.all(), 'number_of_pages': math.ceil(count / limit)}
