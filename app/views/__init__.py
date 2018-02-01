from flask_mail import Message
from app import mail, app
from flask import jsonify, request, abort
from functools import wraps
from app.models import User


def send_mail(subject, sender, recipients, text_body):
    """implementation of send_mail from FlaskMail for sending emails
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
        return jsonify({'error': str(exc.code) + ": " + exc.description}), exc.code
    return ret_val
app.handle_http_exception = get_http_exception_handler(app)

def requires_auth(func):
    '''Decorator to auth-protect routes
    '''
    @wraps(func)
    def decorated(*args, **kwargs):
        '''Generic docstring
        '''
        try:
            auth = request.headers["authorization"]
        except Exception as e:
            abort(401)
        user = User.verify_auth_token(auth)
        if user is None:
            abort(401)
            return func(*args, **kwargs)
    return decorated
