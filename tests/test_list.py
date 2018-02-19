"""
ShoppingList Unittests
"""
from tests.base import APITestCases, create_and_login_user, create_list_and_add_item
from tests import app, LIST_DATA


class ListTestCases(APITestCases):
    """
    Test Cases for ShoppingList CRUD functionality
    """

    def test_shoppinglist_creation_fails_given_form_errors(self):
        """Test API can create a shopping list"""
        tkn = create_and_login_user(self.client)
        res0 = self.client.post(
            '/shoppinglists/',
            data={'name': ''},
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res0.status_code, 422)

    def test_successful_shopping_list_creation(self):
        tkn = create_and_login_user(self.client)
        res1 = self.client.post(
            '/shoppinglists/',
            data=LIST_DATA,
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res1.status_code, 201)

    def test_shoppinglist_deletion_fails_given_list_doesnt_exist(self):
        """Test API can delete an existing shopping list"""
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.delete(
            '/shoppinglists/2',
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res1.status_code, 404)

    def test_successful_shopping_list_deletion(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res2 = self.client.delete(
            '/shoppinglists/1',
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res2.status_code, 200)

    def test_shoppinglist_edit_fails_given_form_errors(self):
        """Test API can edit an existing shopping list"""
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res0 = self.client.put(
            '/shoppinglists/1',
            data={'name': ''},
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res0.status_code, 422)

    def test_shoppinglist_edit_fails_given_list_doesnt_exit(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.put(
            '/shoppinglists/2',
            data={'name': 'testListEdit'},
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res1.status_code, 404)

    def test_api_can_successfully_edit_shopping_list(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res2 = self.client.put(
            '/shoppinglists/1',
            data={'name': 'testListEdit'},
            headers={
                'Content': 'Application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res2.status_code, 201)

    def test_fetching_list_returns_404_given_no_lists(self):
        """Test API returns 404 if retrieving unexistent lists
        """
        tkn = create_and_login_user(self.client)
        res0 = self.client.get(
            '/shoppinglists/', headers={
                'Authorization': tkn
            })
        print(res0)
        self.assertEqual(res0.status_code, 404)

    def test_api_can_fetch_all_lists_two(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res0 = self.client.get(
            '/shoppinglists/', headers={
                'Authorization': tkn
            })
        self.assertEqual(res0.status_code, 200)

    def test_api_can_search_lists(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res1 = self.client.get(
            '/shoppinglists/?q=t', headers={
                'Authorization': tkn
            })
        self.assertEqual(res1.status_code, 200)

    def test_searching_lists_fail_with_wrong_query(self):
        tkn = create_and_login_user(self.client)
        create_list_and_add_item(self.client, tkn)
        res2 = self.client.get(
            '/shoppinglists/?q=z', headers={
                'Authorization': tkn
            })
        self.assertEqual(res2.status_code, 404)
        with app.test_client() as client:
            res0 = client.get('/shoppinglists/')
            self.assertEqual(res0.status_code, 401)
