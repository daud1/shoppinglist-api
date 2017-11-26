"""Database models for User, List and Item tables"""
import math

from flask_login import UserMixin, current_user

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy import func

from app import APP, DB, BCRPT, BCRYPT_LOG_ROUNDS



class User(DB.Model, UserMixin):
    """This class represents the user table"""
    __tablename__ = 'user'
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(255), unique=True)
    password = DB.Column(DB.String(255))
    token = DB.Column(DB.String(255), nullable=True)
    lists = DB.relationship('ShoppingList', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = BCRPT.generate_password_hash(
            password, BCRYPT_LOG_ROUNDS).decode()

    def generate_auth_token(self, expiration=10800):
        """method to generate an authorisation token for user on successful login"""
        ser = Serializer(APP.config['SECRET_KEY'], expires_in=expiration)
        return ser.dumps({'id': self.id})

    def __repr__(self):
        return '<Email %r>' % self.email

    @staticmethod
    def verify_auth_token(token):
        """method to verify authorisation token"""
        ser = Serializer(APP.config['SECRET_KEY'])
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

class ShoppingList(DB.Model):
    """This class represents the shopping_list table"""
    __tablename__ = 'shopping_list'
    id = DB.Column(DB.Integer, primary_key=True)
    list_name = DB.Column(DB.String(64), unique=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey(
        'user.id', ondelete='CASCADE'))

    def __init__(self, list_name, user_id):
        self.list_name = list_name
        self.user_id = user_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'list_name': self.list_name}

    @staticmethod
    def search(que, page=1):
        """This method implements search and pagination."""
        all_lists = ShoppingList.query.filter_by(id=current_user.id)
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

class Item(DB.Model):
    """This class represents the item table"""
    __tablename__ = 'items'
    item_id = DB.Column(DB.Integer, primary_key=True)
    item_name = DB.Column(DB.String(32))
    quantity = DB.Column(DB.Integer)
    list_id = DB.Column(DB.Integer, DB.ForeignKey(
        'shopping_list.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, item_name, list_id, quantity=1):
        self.item_name = item_name
        self.list_id = list_id
        self.quantity = quantity

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'item_name': self.item_name, 'list_id': self.list_id}

    @staticmethod
    def search(que, id, page=1):
        """This method implements search and pagination."""
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

DB.create_all()
