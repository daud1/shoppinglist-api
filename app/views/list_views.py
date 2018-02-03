"""
ShoppingList Routes and View-Functions
"""
# from flasgger import swag_from
from flask import jsonify, request

from app import app
from app.forms import NewListForm
from app.models import Item, ShoppingList, db
from flask_login import current_user
from . import requires_auth


# @swag_from('/swagger_docs/list/view_lists.yml')
@app.route('/shoppinglists/', methods=['GET'])
@requires_auth
def view_all_lists():
    """This function displays all of a User's ShoppingLists."""
    if request.args.get("q"):
        all_sh_lists = ShoppingList.search(
            request.args.get("q"), request.args.get("page"))
        if all_sh_lists['lists']:
            response = jsonify(
                [obj.serialize for obj in all_sh_lists["lists"]])
            response.status_code = 200
            return response
        else:
            response = jsonify({'ERR': 'List does not exist'})
            response.status_code = 404
            return response
    else:
        all_sh_lists = ShoppingList.query.filter_by(
            user_id=current_user.get_id())
        lists = [obj.serialize for obj in all_sh_lists]
        if len(lists) != 0:
            response = jsonify(lists)
            response.status_code = 200
        else:
            response = jsonify(
                {'ERR': 'No lists found.', 'current_id': current_user.get_id()})
            response.status_code = 404
    return response


# @swag_from('/swagger_docs/list/create_new_list.yml')
@app.route('/shoppinglists/', methods=['POST'])
@requires_auth
def create_list():
    """This function given creates a ShoppingList object with the title as the string passed."""
    form = NewListForm()
    if form.validate_on_submit():
        new_list = ShoppingList(form.name.data, current_user.get_id())
        print(current_user.get_id())
        if new_list:
            db.session.add(new_list)
            db.session.commit()
            response = jsonify({
                'MSG': 'Successfully created list',
                'list_id': new_list.id
            })
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'List was not created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response


# @swag_from('/swagger_docs/list/edit_list.yml')
@app.route('/shoppinglists/<id>', methods=['PUT'])
@requires_auth
def edit_list(id):
    """Edits given ShoppingList title to string passed in."""
    form = NewListForm()
    if form.validate_on_submit():
        ed_list = ShoppingList.query.filter_by(id=id).first()
        if ed_list is not None:
            ed_list.name = form.name.data
            db.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'List not found.'})
            response.status_code = 404
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response


# @swag_from('/swagger_docs/list/delete_list.yml')
@app.route('/shoppinglists/<id>', methods=['DELETE'])
@requires_auth
def delete_list(id):
    """Deletes a given ShoppingList."""
    del_list = ShoppingList.query.filter_by(id=id).first()
    del_items = Item.query.filter_by(list_id=id).all()
    if del_list is not None:
        db.session.delete(del_list)

        if del_items is not None:
            for item in del_items:
                db.session.delete(item)

        db.session.commit()
        response = jsonify({'MSG': 'Successfully deleted.'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'Requested list was not found'})
        response.status_code = 404
    return response
