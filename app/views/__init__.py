import inspect
from flask_mail import Message
from ...app import mail, app, login_mgr
from flask import jsonify, request, abort
from functools import wraps
from ...app.models import User

def send_mail(subject, sender, recipients, text_body):
    """implementation of the send_mail method from FlaskMail for sending emails
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    mail.send(msg)


# Override the HTTP exception handler.
def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON.
    """
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        """Generic docstring
        """
        exc = handle_http_exception(exception)
        return jsonify({
            'error': str(exc.code) + ": " + exc.description
        }), exc.code

    return ret_val


app.handle_http_exception = get_http_exception_handler(app)


def requires_auth(func):
    """Decorator to auth-protect routes
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        """__docstring__
        """
        try:
            auth = request.headers["Authorization"]
        except Exception as e:
            abort(401)
        usr_id = User.decode_auth_token(auth)
        if not isinstance(usr_id, int):
            abort(401)
        elif 'usr_id' in inspect.getargspec(func).args:
            kwargs['usr_id'] = usr_id
        return func(*args, **kwargs)

    return decorated


@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
