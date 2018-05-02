"""
Initialisation for API Unittests
"""
import unittest
from ..config import TestingConfig
from ..app import app, db
from ..app.views import auth_views, item_views, list_views

app.config.from_object(TestingConfig)

USER_DATA = {'email': 'test@domain.com', 'password': 'test123'}
F_USER_DATA = {'email': 'test@domain.com', 'password': 'test12'}
FF_USER_DATA = {'email': 'test2@domain.com', 'password': 'test123'}
FFF_USER_DATA = {'email': '', 'password': 'test123'}

REG_DATA = {
    'email': 'test@domain.com',
    'password': 'test123',
    'confirm': 'test123'
}
F_REG_DATA = {
    'email': 'test@domain.com',
    'password': 'test123',
    'confirm': 'test12'
}
FF_REG_DATA = {
    'email': 'test@domain',
    'password': 'test123',
    'confirm': 'test12'
}

ITEM_DATA = {'name': 'testItem'}
LIST_DATA = {'name': 'testList'}
