"""API configurations
"""
import os


class Config(object):
    """Base class for configurations
    """
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = False
    DEBUG = True
    MAIL_PASSWORD = ''
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'david.mwebaza@andela.com'
    MAIL_SERVER = 'smtp.gmail.com'
    SECRET_KEY = os.environ.get('SECRET') or 'not_really_secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'postgresql://postgres:1234@localhost:5432/db_five'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # SWAGGER = {
    #     'swagger': '2.0',
    #     'specs_route': './app/views/swagger_docs/',
    #     'tags': [
    #         {
    #             'name': 'Authentication',
    #             'description': 'The basic unit of authentication.'
    #         },
    #         {
    #             'name': 'List',
    #             'description': 'Lists help to group shopping items'
    #         },
    #         {
    #             'name': 'Item',
    #             'description': 'An item added to a shopping list.'
    #         },
    #     ],
    # }
class TestingConfig(Config):
    """Configuration for Testing. Inherits from Config class.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DB_URI') or 'postgresql://postgres:1234@localhost:5432/circle_test'
    TESTING = True
