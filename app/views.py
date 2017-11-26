"""module for flask ShoppingList API routes"""

from flask import jsonify, request
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from sqlalchemy import exc
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from app import APP, BCRPT, BCRYPT_LOG_ROUNDS, DB, MAIL, Message
from app.forms import (ForgotPasswordForm, LoginForm, NewItemForm, NewListForm,
                       ResetPasswordForm, SignUpForm)
from app.models import Item, ShoppingList, User


def send_mail(subject, sender, recipients, text_body):
    """implementation of send_mail from FlaskMail for sending emails"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    MAIL.send(msg)

# Authentication


LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
LOGIN_MANAGER.login_view = 'login'


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    """Returns User object given User's ID"""
    return User.query.get(int(user_id))


@APP.route('/auth/register', methods=['POST'])
def register():
    """This method registers a new User using the email and password"""
    form = SignUpForm()
    if form.validate_on_submit():
        usr = User(str(request.form['email']), str(request.form['password']))
        if usr:
            try:
                DB.session.add(usr)
                DB.session.commit()
            except exc.IntegrityError:
                response = jsonify({'ERR': 'User email already exists, please choose another'})
                response.status_code = 400
                return response
            response = jsonify({'MSG': 'User account successfully created.'})
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
    """This method logs in a registered User and assigns them a Session Token."""
    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=str(request.form['email'])).first()
        if usr:
            usr_temp = usr.serialize
            if BCRPT.check_password_hash(usr_temp['password'], str(request.form['password'])):
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
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 404
    return response


@APP.route('/auth/logout', methods=['POST'])
def logout():
    """This method is used to log out a logged in User."""
    if current_user is not None:
        current_user.token = None
        DB.session.commit()
        logout_user()
        response = jsonify({"success": "You have successfully logged out!"})
        response.status_code = 200
    return response


@APP.route('/auth/forgot-password', methods=['POST'])
def forgotten_password():
    """
    Method to verify email and send password reset link for forgotten password
    """
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form['email']).first()
        ser = Serializer(APP.config['SECRET_KEY'], expires_in=3600)
        token = ser.dumps({'email': user.email})
        password_reset_url = \
            "http://localhost:5000/" \
            "auth/reset_password/" + str(token)
        email_body = \
            "Please follow the link to reset you " \
            "password\n\n" + password_reset_url + "\n\n Please disregard " \
                                                  "the link if you did not request it" \
                                                  "and immediately contact the administrator."
        send_mail('Password Reset Requested',
                  "david.mwebaza@andela.com",
                  [form.email.data],
                  email_body)
        response = jsonify({'MSG': 'Password Reset Email sucessfully sent!'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': str(form.errors) + ':Email doesn\'t exist!'})
        response.status_code = 400
    return response


@APP.route('/auth/reset_password/<token>', methods=['POST'])
def reset(token=None):
    """
    Method to reset user password
    """
    ser = Serializer(APP.config['SECRET_KEY'])

    try:
        data = ser.loads(token)
    except SignatureExpired:
        response = jsonify({'ERR':"Link expired, please request another."})
        response.status_code = 401
        return response
    except BadSignature:
        response = jsonify({'ERR':"Invalid token!..Mschw!"})
        response.status_code = 401
        return response

    form = ResetPasswordForm()
    user_email = data['email']
    if form.validate_on_submit():
        user = User.query.filter_by(email=user_email)
        user.password = BCRPT.generate_password_hash(
            str(request.form['new_password']), BCRYPT_LOG_ROUNDS).decode()
        DB.session.commit()
        response = jsonify({'MSG': 'Successfully reset password!'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 402
    return response

# Routes


@APP.route('/shoppinglists', methods=['GET'])
@login_required
def view_all_lists():
    """This function displays all of a User's ShoppingLists."""
    all_sh_lists = ShoppingList.search(
        request.args.get("q"), request.args.get("page"))
    if all_sh_lists is not None:
        response = jsonify([obj.serialize for obj in all_sh_lists["lists"]])
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'No lists returned.'})
        response.status_code = 404
    return response


@APP.route('/shoppinglists', methods=['POST'])
@login_required
def create_list():
    """This function given creates a ShoppingList object with the title as the string passed."""
    form = NewListForm()
    if form.validate_on_submit():
        new_list = ShoppingList(form.list_name.data, current_user.get_id())
        if new_list:
            DB.session.add(new_list)
            DB.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR' : 'List was not created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': 'List was not created.'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>', methods=['PUT'])
@login_required
def edit_list(id):
    """Edits given ShoppingList title to string passed in."""
    form = NewListForm()
    if form.validate_on_submit():
        ed_list = ShoppingList.query.filter_by(id=id).first()
        if ed_list is not None:
            ed_list.list_name = form.list_name.data
            DB.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'List not found.'})
            response.status_code = 404
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response


@APP.route('/shoppinglists/<id>', methods=['DELETE'])
@login_required
def delete_list(id):
    """Deletes a given ShoppingList."""
    del_list = ShoppingList.query.filter_by(id=id).first()
    del_items = Item.query.filter_by(list_id=id).all()
    if del_list is not None:
        DB.session.delete(del_list)

        if del_items is not None:
            for item in del_items:
                DB.session.delete(item)

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
    """Displays all the items belonging to a given ShoppingList."""
    if request.args.get('q'):
        list_items = Item.search(
            request.args.get("q"), id, request.args.get("page"))
    else:
        list_items = Item.query.filter_by(list_id=id).all()
    if list_items:
        response = jsonify([obj.serialize for obj in list_items])
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'List items not Found'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>/items/', methods=['POST'])
@login_required
def add_item(id):
    """Adds an item to a given ShoppingList."""
    form = NewItemForm()
    if form.validate_on_submit():
        if form.quantity.data is not None:
            new_item = Item(form.item_name.data, id, form.quantity.data)
        else:
            new_item = Item(form.item_name.data, id)
        #consider using exceptions, increasing qunatity for duplicate items
        DB.session.add(new_item)
        DB.session.commit()
        response = jsonify({'MSG': 'Item added to list'})
        response.status_code = 201
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
@login_required
def edit_item(id, item_id):
    """Edits an item on a given ShoppingList to the string passed."""
    form = NewItemForm()
    
    if form.validate_on_submit():
        ed_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
        if ed_item is not None:
            if form.item_name.data:
                ed_item.item_name = form.item_name.data

            if form.quantity.data:
                ed_item.quantity = form.quantity.data 

            if form.quantity.data and form.item_name.data:
                ed_item.item_name = form.item_name.data
                ed_item.quantity = form.quantity.data
        else:
            response = jsonify({'ERR': 'Item does not exist.'})
            response.status_code = 404
            return response
        response = jsonify({'MSG': 'Edited item.'})
        response.status_code = 200
    else:
        response = jsonify({'MSG': form.errors})
        response.status_code = 404
    return response


@APP.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
@login_required
def delete_item(id, item_id):
    """Deletes item from given ShoppingList."""
    del_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
    if del_item:
        DB.session.delete(del_item)
        DB.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR': 'Requested item was not found.'})
        response.status_code = 404
    return response
