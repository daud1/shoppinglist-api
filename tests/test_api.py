"""module for APIAuth test cases"""
import json
import unittest
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import APP, DB, views

USER_DATA = {'email': 'test@domain.com', 'password': 'test123'}
F_USER_DATA = {'email': 'test@domain.com', 'password': 'test12'}
FF_USER_DATA = {'email': 'test2@domain.com', 'password': 'test123'}

REG_DATA = {'email': 'test@domain.com',
            'password': 'test123', 'confirm': 'test123'}
F_REG_DATA = {'email': 'test@domain.com',
              'password': 'test123', 'confirm': 'test12'}

ITEM_DATA = {'item_name': 'testItem'}
LIST_DATA = {'list_name': 'testList'}


def create_and_login_user(client):
    """
    Helper class to register and login user. 
    Returns token for successful login 
    """
    client.post('/auth/register', data=REG_DATA)
    res = client.post('/auth/login', data=USER_DATA)
    res = json.loads(res.data)
    return res['token']


def create_list_and_add_item(client, tkn):
    """
    Helper function to create a list and add an item to it.
    """
    client.post('/shoppinglists', data=LIST_DATA,
                headers={
                    'Content':          'Application/x-www-form-urlencoded',
                    'Authorization':    'Basic %s' % tkn
                })
    client.post('/shoppinglists/1/items/', data=ITEM_DATA,
                headers={
                    'Content':          'Application/x-www-form-urlencoded',
                    'Authorization':    'Basic %s' % tkn
                })


class APIAuthTestCases(unittest.TestCase):
    """Test cases for API Authentication functionality"""

    def setUp(self):
        """initialisation of variables"""
        APP.testing = True
        self.client = APP.test_client

        APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/test_db'
        APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        with APP.app_context():
            DB.create_all()

    def test_user_register(self):
        """Test API can register a new user"""
        res0 = self.client().post('/auth/register', data=REG_DATA)
        self.assertEqual(res0.status_code, 201)
        res1 = self.client().post('/auth/register', data=F_REG_DATA)
        self.assertEqual(res1.status_code, 400)

    def test_user_login(self):
        """Test API can login registered user"""
        with APP.test_client() as client:
            client.post('/auth/register', data=REG_DATA)
            res0 = client.post('/auth/login', data=F_USER_DATA)
            self.assertEqual(res0.status_code, 401)
            res1 = client.post('/auth/login', data=FF_USER_DATA)
            self.assertEqual(res1.status_code, 404)
            res2 = client.post('/auth/login', data=USER_DATA)
            self.assertEqual(res2.status_code, 200)

    def test_user_logout(self):
        """Test API can logout logged in user"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            res1 = client.post('/auth/logout',
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
                               })
            self.assertEqual(res1.status_code, 200)

    def test_password_forgotten_route(self):
        """
        Test API can send password reset link to email for forgotten passwords
        """
        with APP.test_client() as client:
            create_and_login_user(client)
            res0 = client.post('/auth/forgot-password',
                               data={'email': ''})
            self.assertEqual(res0.status_code, 400)
            res1 = client.post('/auth/forgot-password',
                               data={'email': USER_DATA['email']})
            self.assertEqual(res1.status_code, 200)
            res2 = client.post('/auth/forgot-password',
                               data={'email': 'test23@domain.com'})
            self.assertEqual(res2.status_code, 400)
            res3 = client.post('/auth/forgot-password',
                               data={'email': 'test@'})
            self.assertEqual(res3.status_code, 400)

    def test_password_reset_route(self):
        """Test API can reset forgotten password."""
        with APP.test_client() as client:
            client.post('/auth/register', data=REG_DATA)
            res1 = client.post('/auth/reset_password/daudi')
            self.assertEqual(res1.status_code, 401)
            # time.sleep(60)
            ser = Serializer(APP.config['SECRET_KEY'], expires_in=-60)
            token = ser.dumps({'email': 'test@domain.com'})
            password_reset_url = "/auth/reset_password/" + token.decode("utf-8")
            res2 = client.post(password_reset_url)
            self.assertEqual(res2.status_code, 401)
        
            ser = Serializer(APP.config['SECRET_KEY'], expires_in=360)
            token = ser.dumps({'email': 'test@domain.com'})
            password_reset_url = "/auth/reset_password/" + token.decode("utf-8")
            res0 = client.post(password_reset_url, data={"new_password": 123, "confirm": 123})
            print(res0.data)
            self.assertEqual(res0.status_code, 200)

    def test_shoppinglist_creation(self):
        """Test API can create a shopping list"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            res0 = client.post('/shoppinglists', data={'list_name': ''},
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn})
            self.assertEqual(res0.status_code, 400)
            res1 = client.post('/shoppinglists', data=LIST_DATA,
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
                               })
            self.assertEqual(res1.status_code, 201)

    def test_shoppinglist_deletion(self):
        """Test API can delete an existing shopping list"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res1 = client.delete('/shoppinglists/2',
                                 headers={
                                     'Content':          'Application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % tkn
                                 })
            self.assertEqual(res1.status_code, 404)
            res2 = client.delete('/shoppinglists/1',
                                 headers={
                                     'Content':          'Application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % tkn
                                 })
            self.assertEqual(res2.status_code, 204)

    def test_shoppinglist_edit(self):
        """Test API can edit an existing shopping list"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.put('/shoppinglists/1',
                              data={'list_name':     ''},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res0.status_code, 422)
            res1 = client.put('/shoppinglists/2',
                              data={'list_name':     'testListEdit'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res1.status_code, 404)
            res2 = client.put('/shoppinglists/1', data={'list_name': 'testListEdit'},
                              headers={
                'Content':          'Application/x-www-form-urlencoded',
                'Authorization':    'Basic %s' % tkn
            })
            self.assertEqual(res2.status_code, 201)

    def test_api_can_get_all_lists(self):
        """Test API can retrieve all existing lists"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res1 = client.get('/shoppinglists',
                              headers={
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res1.status_code, 200)
        with APP.test_client() as client:
            res0 = client.get('/shoppinglists')
            self.assertEqual(res0.status_code, 302)

    def test_api_can_get_all_items(self):
        """Test API can display all items on a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.get('/shoppinglists/1',
                              headers={
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res0.status_code, 200)
            with APP.test_client() as client:
                res0 = client.get('/shoppinglists/1')
                self.assertEqual(res0.status_code, 302)

    def test_api_add_item(self):
        """Test API can add items to a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            client.post('/shoppinglists', data=LIST_DATA,
                        headers={
                            'Content':          'Application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % tkn
                        })
            res0 = client.post('/shoppinglists/1/items/', data={'item_name': ''},
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
            })
            self.assertEqual(res0.status_code, 400)
            res1 = client.post('/shoppinglists/1/items/', data=ITEM_DATA,
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
                               })
            self.assertEqual(res1.status_code, 201)

    def test_api_delete_item(self):
        """Test API can delete items from a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.delete('/shoppinglists/1/items/2',
                                 headers={
                                     'Content':          'Application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % tkn
                                 })
            self.assertEqual(res0.status_code, 404)
            res1 = client.delete('/shoppinglists/1/items/1',
                                 headers={
                                     'Content':          'Application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % tkn
                                 })
            self.assertEqual(res1.status_code, 204)

    def test_api_edit_item(self):
        """Test API can edit items on a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.put('/shoppinglists/1/items/1',
                              data={'item_name':     ''},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res0.status_code, 404)
            res1 = client.put('/shoppinglists/1/items/2',
                              data={'item_name':     'testItemEdit'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res1.status_code, 404)
            res2 = client.put('/shoppinglists/1/items/1',
                              data={'item_name':     'testItemEdit'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res2.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        with APP.app_context():
            DB.session.remove()
            DB.drop_all()
