"""Monolithic module for flask shopping list api. includes multiple modules"""
import math
from flask import jsonify, request
from flask_api import FlaskAPI
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy import exc, func

from forms import LoginForm, NewItemForm, NewListForm, SignUpForm

######################### INIT ##########################

APP = FlaskAPI('__name__')
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/DB_five'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(APP)
APP.config['SECRET_KEY'] = 'not_really_secret'
APP.config['WTF_CSRF_ENABLED'] = False
BCRYPT_LOG_ROUNDS = 12

####################### MODELS ####################################


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
        self.password = Bcrypt().generate_password_hash(
            password, BCRYPT_LOG_ROUNDS).decode()

    def generate_auth_token(self, expiration=10800):
        s = Serializer(APP.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def __repr__(self):
        return '<Email %r>' % self.email

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(APP.config['SECRET_KEY'])
        try:
            data = s.loads(token)
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
    def search(q, page=1):
        all_lists = ShoppingList.query.filter_by(current_user.id)
        count = all_lists.count()
        limit = 10

        if q is not None:
            all_lists = all_lists.filter(
                func.lower(ShoppingList.name).like(
                    "%" + q.lower().strip() + "%")
            )
            count = all_lists.count()
        try:
            page = int(page)
        except Exception:
            page = None

        if page is not None:
            return {'lists': all_lists.paginate(page, limit, False).items, 'number_of_pages': math.ceil(count / limit)}

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
        return {'item_name': self.list_name, 'list_id': self.list_id}

    @staticmethod
    def search(q, page=1):
        all_items = ShoppingList.query.filter_by(current_user.id)
        count = all_items.count()
        limit = 10

        if q is not None:
            all_items = all_items.filter(
                func.lower(ShoppingList.name).like(
                    "%" + q.lower().strip() + "%")
            )
            count = all_items.count()
        try:
            page = int(page)
        except Exception:
            page = None

        if page is not None:
            return {'items': all_items.paginate(page, limit, False).items, 'number_of_pages': math.ceil(count / limit)}
        return {'items': all_items.all(), 'number_of_pages': math.ceil(count / limit)}

####################### LOGIN & LOGOUT ############################


LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
LOGIN_MANAGER.login_view = 'login'


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@APP.route('/auth/register', methods=['POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        usr = User(str(request.form['email']), str(request.form['password']))
        if usr:
            try:
                DB.session.add(usr)
                DB.session.commit()
            except exc.IntegrityError:
                response = jsonify(
                    {'ERR': 'User email already exists, please choose another'})

            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'User wasn\'t created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 400
    return response


@APP.route('/auth/login', methods=['POST'])
def login():
    form = LoginForm()
    usr = User.query.filter_by(email=str(request.form['email'])).first()
    usr_temp = usr.serialize
    if usr:
        if Bcrypt().check_password_hash(usr_temp['password'], str(request.form['password'])):
            tkn = usr.generate_auth_token().decode()
            usr.token = tkn
            DB.session.commit()
            login_user(usr)
            response = jsonify({'MSG': 'Login Successful', 'token': tkn})
            response.status_code = 200
        else:
            response = jsonify({'ERR': 'Incorrect Password'})
            response.status_code = 401
    else:
        response = jsonify({'ERR': 'User does not exist'})
        response.status_code = 404
    return response


@APP.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    if current_user is not None:
        current_user.token = None
        DB.session.commit()
        logout_user()
        response = jsonify({"success": "You have successfully logged out!"})
        response.status_code = 200
    return response

###################### ROUTES ##################


@APP.route('/shoppinglists', methods=['GET'])
@login_required
def view_all_lists():
    all_sh_lists = ShoppingList.search(
        request.args.get("q"), request.args.get("page"))
    if all_sh_lists is not None:
        response = jsonify([obj.serialize for obj in all_sh_lists])
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'No lists returned.'})
        response.status_code = 404
    return response


@APP.route('/shoppinglists', methods=['POST'])
@login_required
def create_list():
    form = NewListForm()
    new_list = ShoppingList(form.list_name.data, current_user.get_id())
    if new_list is not None and form.validate_on_submit():
        DB.session.add(new_list)
        DB.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 201
    else:
        response = jsonify({'ERR': 'List was not created'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>', methods=['PUT'])
@login_required
def edit_list(id):
    form = NewListForm()
    ed_list = ShoppingList.query.filter_by(id=id).first()
    if ed_list is not None:
        if form.validate_on_submit():
            ed_list.list_name = form.list_name.data
            DB.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': form.errors})
    else:
        response = jsonify({'ERR': 'failed to find list'})
        response.status_code = 404

    return response


@APP.route('/shoppinglists/<id>', methods=['DELETE'])
@login_required
def delete_list(id):
    del_list = ShoppingList.query.filter_by(id=id).first()
    del_items = Item.query.filter_by(list_id=id).all()
    if del_list is not None:
        DB.session.delete(del_list)

        if del_items is not None:
            for item in del_items:
                DB.session.delete(del_items)

        DB.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR': 'Requested list was not found'})
        response.status_code = 404
    return response


@APP.route('/shoppinglists/<id>', methods=['GET'])
@login_required
def view_list(id):
    list_items = Item.search(request.args.get("q"), request.args.get("page"))
    if list_items is not None:
        response = jsonify(list_items)
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'List items not Found'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>/items/', methods=['POST'])
@login_required
def add_item(id):
    form = NewItemForm()
    if form.validate_on_submit():
        if form.quantity.data is not None:
            new_item = Item(form.item_name.data, id, form.quantity.data)
        else:
            new_item = Item(form.item_name.data, id)
    if new_item is not None:
        DB.session.add(new_item)
        DB.session.commit()
        response = jsonify({'MSG': 'Item added to list'})
        response.status_code = 201
    else:
        response.jsonify({'ERR': 'Item wasnt added to list'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
@login_required
def edit_item(id, item_id):
    form = NewItemForm()
    ed_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
    if form.validate_on_submit():
        if form.item_name.data:
            ed_item.item_name = form.item_name.data

        if form.quantity.data:
            ed_item.quantity = form.quantity.data

        if form.quantity.data and form.item_name.data:
            ed_item.item_name = form.item_name.data
            ed_item.quantity = form.quantity.data

        response = jsonify({'MSG': 'Edited item.'})
        response.status_code = 200
    else:
        response = jsonify({'MSG': form.errors})
        response.status_code = 404
    return response


@APP.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
@login_required
def delete_item(id, item_id):
    del_item = Item.query.filter_by(list_id=id, item_id=item_id).one()
    if del_item is not None:
        DB.session.delete(del_item)
        DB.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR': 'Requested item was not found'})
        response.status_code = 404
    return response


# -----------------------------------------------------------------------------------------------------------------------------------------------
DB.create_all()
if __name__ == '__main__':
    APP.run(debug=True)
