import unittest
from shop import ShoppingList, Item

class ShoppingListTestCases(unittest.TestCase):
    def setUp(self):
        self.t_list = ShoppingList('test')
        self.t_item = Item('sugar', 5)

    def test_add_item(self):
        self.t_list.add_item(self.t_item)
        self.assertEqual(len(self.t_list.items), 1, msg='Add Item failed.')

    def test_remove_item(self):
        self.t_list.add_item(self.t_item)
        self.t_list.remove_item(self.t_item.name)
        self.assertEqual(self.t_list.items[self.t_item.name], 4, msg='Remove Item failed')

    def test_show_list(self):
        self.assertIsNotNone(self.t_list.show_list(), msg='Show List should return the List.')