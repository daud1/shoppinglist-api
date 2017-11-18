"""Monolithic module for flask shopping list api. includes multiple modules"""
from flask_api import FlaskAPI
from flask import render_template, url_for, request, redirect, jsonify
from forms import LoginForm, SignUpForm, NewListForm, NewItemForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from flask_login import logout_user, current_user, login_required
from itsdangerous import (TimedJSONWebSignatureSerializer
                           as Serializer, BadSignature, SignatureExpired)
from flask_bcrypt import Bcrypt

######################### INIT ##########################

app = FlaskAPI('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/db_five'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'not_really_secret'
app.config['WTF_CSRF_ENABLED'] = False
BCRYPT_LOG_ROUNDS = 12
####################### MODELS ####################################

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
        self.password = Bcrypt().generate_password_hash(password, BCRYPT_LOG_ROUNDS).decode()
    
    def generate_auth_token(self, expiration = 10800):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    def __repr__(self):
        return '<Email %r>' % self.email

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
    
    @property 
    def serialize(self):
        """Return object data in easily serializeable format"""
        return { 'email': self.email, 'password': self.password }

class ShoppingList(db.Model):
    """This class represents the shopping_list table"""
    __tablename__ = 'shopping_list'
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def __init__(self, list_name, user_id):
        self.list_name = list_name
        self.user_id = user_id
    
    @property 
    def serialize(self):
        """Return object data in easily serializeable format"""
        return { 'list_name': self.list_name }

class Item(db.Model):
    """This class represents the item table"""
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(32))
    quantity = db.Column(db.Integer)
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, item_name, list_id, quantity=1):
        self.item_name = item_name
        self.list_id = list_id
        self.quantity = quantity
    
    @property 
    def serialize(self):
        """Return object data in easily serializeable format"""
        return { 'item_name': self.list_name, 'list_id': self.list_id }

####################### LOGIN & LOGOUT ############################

LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(app)
LOGIN_MANAGER.login_view = 'login'

@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/auth/register', methods=['POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        #check that the email is unique
        usr = User(str(request.form['email']), str(request.form['password']))
        if usr:
            db.session.add(usr)
            db.session.commit()
            response = jsonify({'MSG':'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR':'User wasn\'t created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 400
    return response

@app.route('/auth/login', methods=['POST'])
def login():
    form = LoginForm()
    usr = User.query.filter_by(email=str(request.form['email'])).first()
    usr_temp = usr.serialize
    if usr:
        if Bcrypt().check_password_hash(usr_temp['password'], str(request.form['password'])):
            tkn = usr.generate_auth_token().decode()
            usr.token = tkn
            db.session.commit()
            login_user(usr)
            response = jsonify({'MSG':'Login Successful', 'token': tkn})
            response.status_code = 200
        else:
            response = jsonify({'ERR':'Incorrect Password'})
            response.status_code = 401
    else:
        response = jsonify({'ERR': 'User does not exist'})
        response.status_code = 404
    return response

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    if current_user is not None:
        current_user.token = None
        db.session.commit()
        logout_user()
        response = jsonify({"success": "You have successfully logged out!"})
        response.status_code = 200
    return response

###################### ROUTES ##################

@app.route('/shoppinglists', methods=['GET'])
@login_required
def view_all_lists():
    all_sh_lists = ShoppingList.query.all()
    if all_sh_lists is not None:
        response = jsonify([obj.serialize for obj in all_sh_lists])
        response.status_code = 200
    else:
        response = jsonify({'ERR':'No lists returned.'})
        response.status_code = 404
    return response

@app.route('/shoppinglists', methods=['POST'])
@login_required
def create_list():
    form = NewListForm()   
    new_list = ShoppingList(form.list_name.data, current_user.get_id())
    if new_list is not None and form.validate_on_submit():
        db.session.add(new_list)
        db.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 201
    else:
        response = jsonify({'ERR':'List was not created'})                
        response.status_code = 400
    return response

@app.route('/shoppinglists/<id>', methods=['PUT'])
@login_required
def edit_list(id):
    form = NewListForm()
    ed_list = ShoppingList.query.filter_by(id=id).first()
    if ed_list is not None:
        if form.validate_on_submit():
            ed_list.list_name = form.list_name.data
            db.session.commit()
            response = jsonify({'MSG':'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': form.errors})
    else:
        response = jsonify({'ERR':'failed to find list'})
        response.status_code = 404
    
    return response

@app.route('/shoppinglists/<id>', methods = ['DELETE'])
@login_required
def delete_list(id):
    del_list = ShoppingList.query.filter_by(id=id).first()
    del_items = Item.query.filter_by(list_id=id).all()
    if del_list is not None:
        db.session.delete(del_list)

        if del_items is not None:
            for item in del_items:
                db.session.delete(del_items)

        db.session.commit()
        response = jsonify({'MSG':'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR':'Requested list was not found'})
        response.status_code = 404
    return response

@app.route('/shoppinglists/<id>', methods=['GET'])
@login_required
def view_list(id):
    list_items = Item.query.filter_by(list_id=id).all()
    if list_items is not None:
        response = jsonify(list_items)
        response.status_code = 200
    else:
        response = jsonify({'ERR':'List items not Found'})
        response.status_code = 400
    return response

@app.route('/shoppinglists/<id>/items/', methods=['POST'])
@login_required
def add_item(id):
    form = NewItemForm()
    if form.validate_on_submit():
        if form.quantity.data is not None:
            new_item = Item(form.item_name.data, id, form.quantity.data)
        else:
            new_item = Item(form.item_name.data, id)
    if new_item is not None:
        db.session.add(new_item)
        db.session.commit()
        response = jsonify({'MSG': 'Item added to list'})
        response.status_code = 201
    else:
        response.jsonify({'ERR':'Item wasnt added to list'})
        response.status_code = 400
    return response

@app.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
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
        
        response = jsonify({'MSG':'Edited item.'})
        response.status_code = 200
    else:
        response = jsonify({'MSG':form.errors})
        response.status_code = 404
    return response

@app.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
@login_required
def delete_item(id, item_id):
    del_item = Item.query.filter_by(list_id=id, item_id=item_id).one()
    if del_item is not None:
        db.session.delete(del_item)
        db.session.commit()
        response = jsonify({'MSG':'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR':'Requested item was not found'})
        response.status_code = 404
    return response 

# -----------------------------------------------------------------------------------------------------------------------------------------------
db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
