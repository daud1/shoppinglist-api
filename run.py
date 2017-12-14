"""Control script for the ShoppingList API"""
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from app import APP
from app.views import auth_views, list_views, item_views

if __name__ == '__main__':
    APP.run(debug=True)
