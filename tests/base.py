import json
import unittest

from app import app, db
from tests import ITEM_DATA, LIST_DATA, REG_DATA, USER_DATA


class APITestCases(unittest.TestCase):
    """Super Class for API test cases"""

    def setUp(self):
        """initialisation of variables"""
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

def create_and_login_user(client):
    """
    Helper function to register and login user.
    Returns token for successful login.
    """
    client.post('/auth/register', data=REG_DATA)
    res = client.post('/auth/login', data=USER_DATA)
    res = json.loads(res.data)
    return res['token']

def create_user(client):
    """Helper function to register a user
    """
    client.post('auth/register', data=REG_DATA)

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
