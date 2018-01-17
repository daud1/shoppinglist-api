
"""
ShoppingList Item Unittests
"""
from tests import APITestCases, create_and_login_user, create_list_and_add_item
from tests import APP, LIST_DATA, ITEM_DATA


class ItemTestCases(APITestCases):
    """
    Test Cases for ShoppingList Item CRUD functionality
    """

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
            self.assertEqual(res1.status_code, 200)

    def test_api_edit_item(self):
        """Test API can edit items on a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.put('/shoppinglists/1/items/1',
                              data={'name':     ''},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res0.status_code, 422)
            res1 = client.put('/shoppinglists/1/items/2',
                              data={'name':     'testItemEdit'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res1.status_code, 404)
            res2 = client.put('/shoppinglists/1/items/1',
                              data={'name':     'testItemEdit'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res2.status_code, 201)
            res3 = client.put('/shoppinglists/1/items/1',
                              data={'name':     'testItemEdit',
                                    'quantity':      '4'},
                              headers={
                                  'Content':          'Application/x-www-form-urlencoded',
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res3.status_code, 201)

    def test_api_can_get_all_items_one(self):
        """Test API can return error for no items """
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            client.post('/shoppinglists/', data=LIST_DATA,
                        headers={
                            'Content':          'Application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % tkn
                        })
            res = client.get('/shoppinglists/1',
                             headers={'Authorization':    'Basic %s' % tkn})
            self.assertEqual(res.status_code, 404)

    def test_api_can_get_all_items_two(self):
        """Test API can display all items on a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            create_list_and_add_item(client, tkn)
            res0 = client.get('/shoppinglists/1',
                              headers={
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res0.status_code, 200)
            res1 = client.get('/shoppinglists/1?q=t',
                              headers={
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res1.status_code, 200)
            res2 = client.get('/shoppinglists/1?q=z',
                              headers={
                                  'Authorization':    'Basic %s' % tkn
                              })
            self.assertEqual(res2.status_code, 404)
            with APP.test_client() as client:
                res0 = client.get('/shoppinglists/1')
                self.assertEqual(res0.status_code, 302)

    def test_api_add_item(self):
        """Test API can add items to a given shoppinglist"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            client.post('/shoppinglists/', data=LIST_DATA,
                        headers={
                            'Content':          'Application/x-www-form-urlencoded',
                            'Authorization':    'Basic %s' % tkn
                        })
            res0 = client.post('/shoppinglists/1/items/', data={'name': ''},
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
            })
            self.assertEqual(res0.status_code, 422)
            res1 = client.post('/shoppinglists/1/items/', data=ITEM_DATA,
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
                               })
            self.assertEqual(res1.status_code, 201)
