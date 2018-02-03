"""
Authentication Routes and View-Functions
"""
import jwt
# from flasgger import swag_from
from flask import abort, jsonify, request
from flask_login import current_user, login_user, logout_user
from itsdangerous import BadSignature, Serializer, SignatureExpired
from sqlalchemy import exc

from app import app, bcrypt, db, mail
from app.forms import (ForgotPasswordForm, LoginForm, ResetPasswordForm,
                       SignUpForm)
from app.models import User

from . import requires_auth, send_mail

# @swag_from('/swagger_docs/auth/register.yml')
@app.route('/auth/register', methods=['POST'])
def register():
    """This method registers a new User using the email and password"""
    form = SignUpForm()
    if form.validate_on_submit():
        usr = User(str(request.form['email']), str(request.form['password']))
        if usr:
            db.session.add(usr)
            db.session.commit()
            response = jsonify({'MSG': 'User account successfully created.'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'User wasn\'t created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response

# @swag_from('/swagger_docs/auth/login.yml')
@app.route('/auth/login', methods=['POST'])
def login():
    """This method logs in a registered User and assigns them a Session Token."""
    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=str(request.form['email'])).first()
        if usr:
            usr_temp = usr.serialize
            if bcrypt.check_password_hash(usr_temp['password'], str(request.form['password'])):
                login_user(usr)
                tkn = usr.encode_auth_token()
                usr.token = tkn
                db.session.commit()
                response = jsonify({'MSG': 'Login Successful', 'token': tkn.decode()})
                response.status_code = 200
            else:
                response = jsonify({'ERR': 'Incorrect Password'})
                response.status_code = 401
        else:
            response = jsonify({'ERR': 'User doesn\'t exist.'})
            response.status_code = 404
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response

# @swag_from('/swagger_docs/auth/logout.yml')
@app.route('/auth/logout', methods=['POST'])
@requires_auth
def logout():
    """This method is used to log out a logged in User."""
    if current_user is not None:
        current_user.token = None
        db.session.commit()
        logout_user()
        response = jsonify({"success": "You have successfully logged out!"})
        response.status_code = 200
    return response

# @swag_from('/swagger_docs/auth/forgot_password.yml')
@app.route('/auth/forgot-password', methods=['POST'])
def forgotten_password():
    """
    Method to verify email and send password reset link to email
    """
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form['email']).first()
        token = user.encode_auth_token()
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
                  email_body
                  )
        
        response = jsonify({'MSG': 'Password Reset Email sucessfully sent!'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': str(form.errors)})
        response.status_code = 422
    return response

# @swag_from('/swagger_docs/auth/reset_password.yml')
@app.route('/auth/reset_password/<token>', methods=['POST'])
def reset(token=None):
    """
    Method to reset user password
    """
    try:
        payload = jwt.decode(token, app.config.get('SECRET_KEY'))
        print(payload)
    except jwt.ExpiredSignatureError:
        response = jsonify({'ERR': "Link expired, please request another."})
        response.status_code = 401
        return response    
    except jwt.InvalidTokenError:
        response = jsonify({'ERR': "Invalid token!..Mschw!"})
        response.status_code = 401
        return response

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=payload['sub'])
        user.password = bcrypt.generate_password_hash(
            str(request.form['new_password']), app.config['BCRYPT_LOG_ROUNDS']).decode()
        db.session.commit()
        response = jsonify({'MSG': 'Successfully reset password!'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response
