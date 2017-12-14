"""
Initialisation and configs for the ShoppingList API
"""
from functools import wraps

from flasgger import Swagger
from flasgger.utils import swag_from
from flask import jsonify, redirect, request
from flask_api import FlaskAPI
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from .forms import (ForgotPasswordForm, LoginForm, NewItemForm, NewListForm,
                   ResetPasswordForm, SignUpForm)

from .models import DB, Item, ShoppingList, User
from .views import auth_views, item_views, list_views

APP = FlaskAPI('__name__')

BCRPT = Bcrypt(APP)
BCRYPT_LOG_ROUNDS = 12

MAIL = Mail(APP)

LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
LOGIN_MANAGER.login_view = 'login'

Swagger(APP)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/db_five'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SECRET_KEY'] = 'not_really_secret'
APP.config['WTF_CSRF_ENABLED'] = False

APP.config['SWAGGER'] = {
    'swagger': '2.0',
    'specs_route': '/swagger_docs/',
    'tags': [
        {
            'name': 'Authentication',
            'description': 'The basic unit of authentication.'
        },
        {
            'name': 'List',
            'description': 'Lists help to group shopping items'
        },
        {
            'name': 'Item',
            'description': 'An item added to a shopping list.'
        },
    ],
}
APP.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='david.mwebaza@andela.com',
    MAIL_PASSWORD='cr3{tW4ve',
))

def send_mail(subject, sender, recipients, text_body):
    """implementation of send_mail from FlaskMail for sending emails"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    MAIL.send(msg)


def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        """
        Generic docstring
        """
        exc = handle_http_exception(exception)
        return jsonify({'error': str(exc.code) + ": " + exc.description}), exc.code
    return ret_val


# Override the HTTP exception handler.
APP.handle_http_exception = get_http_exception_handler(APP)
