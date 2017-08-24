
class ShoppingList(object):
    """class to represent a shopping list and CRUD methods"""
    def __init__(self, name):
        self.name = name
        self.items = {}

    def add_item(self, an_item):
        if an_item.name in self.items:
            self.items[an_item.name] += an_item.quantity
        else:
            self.items[an_item.name] = an_item.quantity

    def remove_item(self, name):
        if name not in self.items:
            print 'Item not on shopping list.'
        else:
            if self.items[name] > 1:#reduce the item numbers by 1 if there's more than 1
                self.items[name] -= 1
            elif self.items[name] == 0 or self.items[name] == 1:#else remove the item from the list entirely
                del self.items[name]
    
    def show_list(self):
        print self.items
        return self.items

    
class Item(object):
    """class to represent items on a shopping list"""
    def __init__(self, name, quantity=1):
        self.name = str(name)
        self.quantity = int(quantity)