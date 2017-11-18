"""module for APIAuth test cases"""
import unittest
import json
from api import app, db


class APIAuthTestCases(unittest.TestCase):
    """Test cases for API Authentication functionality"""

    def setUp(self):
        """initialisation of variables"""
        app.testing = True
        self.client = app.test_client

        self.t_user = {'email': 'test@domain.com', 'password': 'test123'}
        self.t_reg_data = {'email': 'test@domain.com',
                           'password': 'test123', 'confirm': 'test123'}
        self.t_list = {'list_name': 'testList'}
        self.t_item = {'item_name': 'testItem'}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/test_db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        with app.app_context():
            db.create_all()

    def test_user_register(self):
        """Test API can register a new user"""
        res0 = self.client().post('/auth/register', data=self.t_reg_data)
        self.assertEqual(res0.status_code, 201)

    def test_user_login(self):
        """Test API can login registered user"""
        with app.test_client() as client:
            res0 = client.post('/auth/register', data=self.t_reg_data)
            self.assertEqual(res0.status_code, 201)
            res1 = client.post('/auth/login', data=self.t_user)
            self.assertEqual(res1.status_code, 200)

    def test_user_logout(self):
        """Test API can logout logged in user"""
        with app.test_client() as client:
            res0 = client.post('/auth/register', data=self.t_reg_data)
            self.assertEqual(res0.status_code, 201)
            res1 = client.post('auth/login', data=self.t_user)
            self.assertEqual(res1.status_code, 200)
            temp1 = json.loads(res1.data)
            res2 = client.post('auth/logout',
                               headers={
                                   'Content':          'application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % temp1['token']
                               })
            self.assertEqual(res2.status_code, 200)

    def test_shoppinglist_creation(self):
        """Test API can create a shopping list"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            res2 = client.post('/shoppinglists', data=self.t_list,
                               headers={
                                   'Content':          'application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % temp1['token']
                               })
            print(res2.data)
            self.assertEqual(res2.status_code, 201)

    def test_shoppinglist_deletion(self):
        """Test API can delete an existing shopping list"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res3 = client.delete('/shoppinglists/1',
                                 headers={
                                     'Content':          'application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % temp1['token']
                                 })
            self.assertEqual(res3.status_code, 204)

    def test_shoppinglist_edit(self):
        """Test API can edit an existing shopping list"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res3 = client.put('/shoppinglists/1', data={'list_name': 'testList2'},
                              headers={
                'Content':          'application/x-www-form-urlencoded',
                'Authorization':    'Basic %s' % temp1['token']
            })
            self.assertEqual(res3.status_code, 201)

    def test_api_can_get_all_lists(self):
        """Test API can retrieve all existing lists"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res3 = client.get('/shoppinglists',
                              headers={
                                  'Authorization':    'Basic %s' % temp1['token']
                              })
            self.assertEqual(res3.status_code, 200)

    def test_api_can_get_all_items(self):
        """Test API can display all items on a given shoppinglist"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res3 = client.get('/shoppinglists/1',
                              headers={
                                  'Authorization':    'Basic %s' % temp1['token']
                              })
            self.assertEqual(res3.status_code, 200)

    def test_api_add_item(self):
        """Test API can add items to a given shoppinglist"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res3 = client.post('/shoppinglists/1/items/', data=self.t_item,
                               headers={
                                   'Content':          'application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % temp1['token']
                               })
            self.assertEqual(res3.status_code, 201)

    def test_api_delete_item(self):
        """Test API can delete items from a given shoppinglist"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            client.post('/shoppinglists/1/items/', data=self.t_item,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res4 = client.delete('/shoppinglists/1/items/1',
                                 headers={
                                     'Content':          'application/x-www-form-urlencoded',
                                     'Authorization':    'Basic %s' % temp1['token']
                                 })
            self.assertEqual(res4.status_code, 204)
            print(res4.data)

    def test_api_edit_item(self):
        """Test API can edit items on a given shoppinglist"""
        with app.test_client() as client:
            client.post('/auth/register', data=self.t_reg_data)
            res1 = client.post('/auth/login', data=self.t_user)
            temp1 = json.loads(res1.data)
            client.post('/shoppinglists', data=self.t_list,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            client.post('/shoppinglists/1/items/', data=self.t_item,
                        headers={
                            'Content':          'application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % temp1['token']
                        })
            res4 = client.put('/shoppinglists/1/items/1',
                              data={'item_name':     'testItemEdit'},
                              headers={
                                  'Content':          'application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % temp1['token']
                              })
            self.assertEqual(res4.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
