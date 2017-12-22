"""API configurations
"""
import os
class Config(object):
    """Super class for setting Configurations
    """
    DEBUG = True
    CSRF_ENABLED = True
    SECRET = os.environ.get('SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class DevelopmentConfig(Config):
    """Configuration for Development. Inherits from Config class.
    """
    DEBUG = True
    DEVELOPMENT = True

class TestingConfig(Config):
    """Configuration for Testing. Inherits from Config class.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URI')
    DEBUG = True
    SECRET = 'not_really_secret'

APP_CONFIG = {
    'development':  DevelopmentConfig,
    'testing':  TestingConfig,
}
