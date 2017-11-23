"""Control script for the ShoppingList API"""
from app import APP
import app.views

if __name__ == '__main__':
    APP.run(debug=True)
    