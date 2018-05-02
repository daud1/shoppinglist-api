"""
ShoppingList Item Routes and View-Functions
"""
import math

# from flasgger import swag_from
from flask import jsonify, request

from ...app import app
from ...app.forms import NewItemForm
from ...app.models import Item, db

from . import requires_auth


# @swag_from('/swagger_docs/item/view_list_items.yml')
@app.route('/shoppinglists/<id>', methods=['GET'])
@requires_auth
def view_list(id):
    """Displays all the items belonging to a given ShoppingList.
    """
    try:
        page = int(request.args.get("page"))
    except Exception as e:
        print(str(e))
        page = 1
        
    if request.args.get('q'):
        list_items = Item.search(
            request.args.get("q"), id, page)
        if list_items['items']:
            response = jsonify({
                'items': [obj.serialize for obj in list_items['items']],
                'number_of_pages': list_items['number_of_pages']
                })
            response.status_code = 200
            return response
        else:
            response = jsonify({'ERR': 'List items not found.:('})
            response.status_code = 404
            return response
            
    else:
        listItems = Item.query.filter_by(list_id=id)
        limit = int(7)
        items = listItems.paginate(page, limit).items
        items = [obj.serialize for obj in items]
        count = len(listItems.all())
        if len(items) != 0:
            response = jsonify({
                'items': items,
                'number_of_pages': math.ceil(count / limit)
            })
            response.status_code = 200
        else:
            response = jsonify({'ERR': 'No List Items found.'})
            response.status_code = 404
    return response


# @swag_from('/swagger_docs/item/create_new_list_item.yml')
@app.route('/shoppinglists/<id>/items/', methods=['POST'])
@requires_auth
def add_item(id):
    """Adds an item to a given ShoppingList."""
    form = NewItemForm()
    if form.validate_on_submit():
        new_item = Item.query.filter_by(name=(form.name.data).lower(), list_id=id).first()
        if not new_item:
            new_item = Item(form.name.data, id)
            if new_item:
                db.session.add(new_item)
                db.session.commit()
                response = jsonify({'MSG': 'Item added to list'})
                response.status_code = 201
            else:
                response = jsonify({'ERR': 'Oops, something went wrong. Try again!'})
                response.status_code = 400
        else:
            response = jsonify({'ERR': 'Item already exists!'})
            response.status_code = 409
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response


# @swag_from('/swagger_docs/item/edit_list_items.yml')
@app.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
@requires_auth
def edit_item(id, item_id):
    """Edits an item on a given ShoppingList to the string passed."""
    form = NewItemForm()

    if form.validate_on_submit():
        ed_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
        if ed_item is not None:
            if form.name.data:
                ed_item.name = form.name.data
                db.session.commit()
        else:
            response = jsonify({'ERR': 'Item does not exist.'})
            response.status_code = 404
            return response
        response = jsonify({'MSG': 'Edited item.'})
        response.status_code = 201
    else:
        response = jsonify({'MSG': form.errors})
        response.status_code = 422
    return response


# @swag_from('/swagger_docs/item/delete_list_items.yml')
@app.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
@requires_auth
def delete_item(id, item_id):
    """Deletes item from given ShoppingList."""
    del_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
    if del_item:
        db.session.delete(del_item)
        db.session.commit()
        response = jsonify({'MSG': 'Successfully deleted.'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'Requested item was not found.'})
        response.status_code = 404
    return response
