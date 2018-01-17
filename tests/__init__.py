"""
Initialisation for API Unittests
"""
import json
import unittest
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.setup import APP
from app.models import DB
from app.views import list_views, item_views, auth_views

USER_DATA = {'email': 'test@domain.com', 'password': 'test123'}
F_USER_DATA = {'email': 'test@domain.com', 'password': 'test12'}
FF_USER_DATA = {'email': 'test2@domain.com', 'password': 'test123'}
FFF_USER_DATA = {'email': '', 'password': 'test123'}

REG_DATA = {'email': 'test@domain.com',
            'password': 'test123', 'confirm': 'test123'}
F_REG_DATA = {'email': 'test@domain.com',
              'password': 'test123', 'confirm': 'test12'}
FF_REG_DATA = {'email': 'test@domain',
               'password': 'test123', 'confirm': 'test12'}

ITEM_DATA = {'name': 'testItem'}
LIST_DATA = {'name': 'testList'}


def create_and_login_user(client):
    """
    Helper class to register and login user.
    Returns token for successful login.
    """
    client.post('/auth/register', data=REG_DATA)
    res = client.post('/auth/login', data=USER_DATA)
    res = json.loads(res.data)
    return res['token']


def create_list_and_add_item(client, tkn):
    """
    Helper function to create a list and add an item to it.
    """
    client.post('/shoppinglists/', data=LIST_DATA,
                headers={
                    'Content':          'Application/x-www-form-urlencoded',
                    'Authorization':    'Basic %s' % tkn
                })
    client.post('/shoppinglists/1/items/', data=ITEM_DATA,
                headers={
                    'Content':          'Application/x-www-form-urlencoded',
                    'Authorization':    'Basic %s' % tkn
                })


class APITestCases(unittest.TestCase):
    """Super Class for API test cases"""

    def setUp(self):
        """initialisation of variables"""
        APP.testing = True
        self.client = APP.test_client

        APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/test_db'
        APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        with APP.app_context():
            DB.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with APP.app_context():
            DB.session.remove()
            DB.drop_all()
