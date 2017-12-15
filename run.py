"""Run script for the ShoppingList API
"""
from app import APP
from app.views import auth_views, list_views, item_views

if __name__ == '__main__':
    APP.run(debug=True)
