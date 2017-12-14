"""
ShoppingList Routes and View-Functions
"""
from app.forms import NewListForm
from app.models import DB, Item, ShoppingList
from app.setup import (APP, current_user, jsonify, login_required, request,
                        swag_from)


@APP.route('/shoppinglists', methods=['GET'])
@login_required
def view_all_lists():
    """This function displays all of a User's ShoppingLists."""
    all_sh_lists = ShoppingList.search(
        request.args.get("q"), request.args.get("page"))
    if all_sh_lists is not None:
        response = jsonify([obj.serialize for obj in all_sh_lists["lists"]])
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'No lists returned.'})
        response.status_code = 404
    return response


@APP.route('/shoppinglists', methods=['POST'])
@login_required
@swag_from('swagger_docs/list/create_new_list.yml')
def create_list():
    """This function given creates a ShoppingList object with the title as the string passed."""
    form = NewListForm()
    if form.validate_on_submit():
        new_list = ShoppingList(form.list_name.data, current_user.get_id())
        if new_list:
            DB.session.add(new_list)
            DB.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'List was not created.'})
            response.status_code = 400
    else:
        response = jsonify({'ERR': 'List was not created.'})
        response.status_code = 400
    return response


@APP.route('/shoppinglists/<id>', methods=['PUT'])
@login_required
@swag_from('swagger_docs/list/edit_list.yml')
def edit_list(id):
    """Edits given ShoppingList title to string passed in."""
    form = NewListForm()
    if form.validate_on_submit():
        ed_list = ShoppingList.query.filter_by(id=id).first()
        if ed_list is not None:
            ed_list.list_name = form.list_name.data
            DB.session.commit()
            response = jsonify({'MSG': 'Success'})
            response.status_code = 201
        else:
            response = jsonify({'ERR': 'List not found.'})
            response.status_code = 404
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response


@APP.route('/shoppinglists/<id>', methods=['DELETE'])
@login_required
@swag_from('swagger_docs/list/delete_list.yml')
def delete_list(id):
    """Deletes a given ShoppingList."""
    del_list = ShoppingList.query.filter_by(id=id).first()
    del_items = Item.query.filter_by(list_id=id).all()
    if del_list is not None:
        DB.session.delete(del_list)

        if del_items is not None:
            for item in del_items:
                DB.session.delete(item)

        DB.session.commit()
        response = jsonify({'MSG': 'Success'})
        response.status_code = 204
    else:
        response = jsonify({'ERR': 'Requested list was not found'})
        response.status_code = 404
    return response