from flask import Flask, render_template, url_for, request, redirect, jsonify
from forms import LoginForm, SignUpForm, NewListForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

            ######################### initialisation ##########################
app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/db_three'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'not_really_secret'


            ####################### LOGIN & LOGOUT ############################
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

            ####################### MODELS ####################################
class User(db.Model, UserMixin):
    """This class represents the user table"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(16))
    lists = db.relationship('ShoppingList', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = password


class ShoppingList(db.Model):
    """This class represents the shopping_list table"""
    __tablename__ = 'shopping_list'
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, list_name):
        self.list_name = list_name

class Item(db.Model):
    """This class represents the item table"""
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(32))
    quantity = db.Column(db.Integer)
    list_name = db.Column(db.String(64), db.ForeignKey('shopping_list.list_name'))

    def __init__(self, item_name, list_name, quantity=1):
        self.item_name = item_name
        self.list_name = list_name
        self.quantity = quantity

            ###################### views and routing functions##################

###crud lists###
@app.route('/shop/login')
@app.route('/index', methods=['GET/', 'POST'])
def index():
    form = LoginForm()
    if request.method =='POST':
        usr = User.query.filter_by(email=str(request.form['email'])).first()
        if usr:
            if usr.password == form.password.data:
                login_user(usr)
                return redirect(url_for('view_all_lists'))
    return render_template('index', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit:
        usr = User(str(form.email.data), str(form.data.password))
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/shoppinglist', methods=['GET'])
def view_all_lists():
    all_sh_lists = ShoppingList.query.all()
    if all_sh_lists:
        response = jsonify(all_sh_lists)
        response.status_code = 200
    else:
        response = jsonify({'ERR':'No lists returned.'})
        response.status_code = 404
    return response

@app.route('/shoppinglist', methods=['POST'])
def create_list():
    form = NewListForm()   
    new_list = ShoppingList(request.form['list_name'])
    if new_list is not None:
        db.session.add(new_list)
        db.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 201
    else:
        response = jsonify({'ERR':'List was not created'})                
        response.status_code = 400
    return response

@app.route('/shoppinglist/<id>', methods = ['DELETE'])
def delete_list(id):
    del_list = ShoppingList.query.filter_by(id=id).one()
    if del_list is not None:
        db.session.delete(del_list)
        db.session.commit()
        response = jsonify({'MSG':'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR':'Requested list was not found'})
        response.status_code = 404
    return response

@app.route('/shoppinglist/<id>', methods=['GET'])
def view_single_list(id):
    single_list = ShoppingList.query.filter_by(id=id)
    if single_list is not None:
        response = jsonify(single_list)
        response = 200
    else:
        response = jsonify({'ERR':'List not Found'})
        response = 404
    return response

# @app.route('/add_item', methods=['POST'])
# def add_item():    
#     return redirect(url_for('view_list', name=list_name))

# @app.route('/del_item')
# def del_item():
#     return redirect(url_for('view_list', name=list_name))

# @app.route('/view_list/<string:name>')
# def view_list(name):
#     sh_list = Item.item_name.query.filter_by(list_name=name)
#     return render_template('view_list.html', list=sh_list)
# -----------------------------------------------------------------------------------------------------------------------------------------------
db.create_all()
if __name__ == '__main__':
    app.run(debug=True)