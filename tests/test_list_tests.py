"""
ShoppingList Unittests
"""
from tests import APITestCases, create_and_login_user, create_list_and_add_item
from tests import APP, LIST_DATA


class ListTestCases(APITestCases):
    """
    Test Cases for ShoppingList CRUD functionality
    """

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
