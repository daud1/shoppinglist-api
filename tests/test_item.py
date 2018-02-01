
"""
ShoppingList Item Unittests
"""
from tests import ITEM_DATA, LIST_DATA, app
from tests.base import (APITestCases, create_and_login_user,
                        create_list_and_add_item)

class ItemTestCases(APITestCases):
    """
    Test Cases for ShoppingList Item CRUD functionality
    """

    def test_item_deletion_fails_given_item_doesnt_exist(self):
        """Test API can delete items from a given shoppinglist"""
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res0 = self.client.delete('/shoppinglists/1/items/2',
                                headers={
                                    'Content':          'Application/x-www-form-urlencoded',
                                    'Authorization':    'Basic %s' % tkn
                                })
        self.assertEqual(res0.status_code, 404)

    def test_successful_item_deletion(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.delete('/shoppinglists/1/items/1',
                                headers={
                                    'Content':          'Application/x-www-form-urlencoded',
                                    'Authorization':    'Basic %s' % tkn
                                })
        self.assertEqual(res1.status_code, 200)

    def test_item_edit_fails_given_form_errors(self):
        """Test API can edit items on a given shoppinglist"""
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res0 = self.client.put('/shoppinglists/1/items/1',
                            data={'name':     ''},
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res0.status_code, 422)

    def test_item_edit_fails_given_item_doesnt_exist(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.put('/shoppinglists/1/items/2',
                            data={'name':     'testItemEdit'},
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res1.status_code, 404)

    def test_successful_item_title_edit(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res2 = self.client.put('/shoppinglists/1/items/1',
                            data={'name':     'testItemEdit'},
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res2.status_code, 201)

    def test_successful_item_quantity_edit(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res3 = self.client.put('/shoppinglists/1/items/1',
                            data={
                                'name':     'testItemEdit',
                                'quantity':   '4'
                            },
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res3.status_code, 201)

    def test_fetching_items_given_list_doesnt_exist(self):
        """Test API can return error for no items """
        tkn = create_and_login_user(self.client)
        self.client.post('/shoppinglists/', data=LIST_DATA,
                    headers={
                        'Content':          'Application/x-www-form-urlencoded',
                        'Authorization':    'Basic %s' % tkn
                    })
        res = self.client.get('/shoppinglists/1',
                            headers={'Authorization':    'Basic %s' % tkn})
        self.assertEqual(res.status_code, 404)

    def test_successful_item_fetch(self):
        """Test API can display all items on a given shoppinglist"""
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res0 = self.client.get('/shoppinglists/1',
                            headers={
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res0.status_code, 200)

    def test_successful_item_search(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.get('/shoppinglists/1?q=t',
                            headers={
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res1.status_code, 200)

    def test_item_search_fails_given_item_doesnt_exist(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res2 = self.client.get('/shoppinglists/1?q=z',
                            headers={
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res2.status_code, 404)
        with app.test_client() as client:
            res0 = client.get('/shoppinglists/1')
            self.assertEqual(res0.status_code, 302)

    def test_adding_item_fails_given_form_errors(self):
        """Test API can add items to a given shoppinglist"""
        tkn = create_and_login_user(self.client)
        self.client.post('/shoppinglists/', data=LIST_DATA,
                    headers={
                        'Content':          'Application/x-www-form-urlencoded',
                        'Authorization':    'Basic %s' % tkn
                    })
        res0 = self.client.post('/shoppinglists/1/items/', data={'name': ''},
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
        })
        self.assertEqual(res0.status_code, 422)

    def test_successful_item_creation(self):
        tkn = create_and_login_user(self.client)
        self.client.post('/shoppinglists/', data=LIST_DATA,
                    headers={
                        'Content':          'Application/x-www-form-urlencoded',
                        'Authorization':    'Basic %s' % tkn
                    })
        res1 = self.client.post('/shoppinglists/1/items/', data=ITEM_DATA,
                            headers={
                                'Content':          'Application/x-www-form-urlencoded',
                                'Authorization':    'Basic %s' % tkn
                            })
        self.assertEqual(res1.status_code, 201)
