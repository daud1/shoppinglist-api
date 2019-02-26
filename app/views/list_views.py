"""
ShoppingList Routes and View-Functions
"""
import math

# from flasgger import swag_from
from flask import jsonify, request
from flask_login import current_user, login_required

from app import app
from app.forms import NewListForm
from app.models import Item, ShoppingList, db

from app.views import requires_auth


# @swag_from('/swagger_docs/list/view_lists.yml')
@app.route('/shoppinglists/', methods=['GET'])
@requires_auth
def view_all_lists(usr_id):
    """This function displays all of a User's ShoppingLists.
    """
    try:
        page = int(request.args.get("page"))
    except Exception as e:
        print(str(e))
        page = 1

    if request.args.get("q"):
        all_sh_lists = ShoppingList.search(
            request.args.get("q"), usr_id, page)
        if all_sh_lists['lists']:
            response = jsonify({
                'lists': [obj.serialize for obj in all_sh_lists['lists']],
                'number_of_pages': all_sh_lists['number_of_pages']
                })
            response.status_code = 200
            return response
        else:
            response = jsonify({'ERR': 'List does not exist.'})
            response.status_code = 404
            return response
    else:
        all_sh_lists = ShoppingList.query.filter_by(user_id=usr_id)
        limit = int(10)
        lists = all_sh_lists.paginate(page, limit).items
        lists = [obj.serialize for obj in lists]
        count = len(all_sh_lists.all())
        if len(lists) != 0:
            response = jsonify({
                'lists': lists,
                'number_of_pages': math.ceil(count / limit)
            })
            response.status_code = 200
        else:
            response = jsonify({'ERR': 'No lists found.', 'id': usr_id})
            response.status_code = 404
    return response


# @swag_from('/swagger_docs/list/create_new_list.yml')
@app.route('/shoppinglists/', methods=['POST'])
@requires_auth
def create_list(usr_id):
    """This function given creates a ShoppingList object with the title as the string passed."""
    form = NewListForm()
    if form.validate_on_submit():
        new_list = ShoppingList(form.name.data, usr_id)
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
