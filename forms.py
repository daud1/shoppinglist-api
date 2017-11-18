"""module for shoppinglist-api forms"""
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Email
from wtforms import TextField, PasswordField, IntegerField, StringField


class LoginForm(FlaskForm):
    """class to represent the login form"""
    email = TextField('Email Address', validators=[
        DataRequired(message='Please enter an email address')])
    password = PasswordField('Enter Password', validators=[
        DataRequired('Please enter your password')])


class SignUpForm(FlaskForm):
    """class to represent the sign-up form"""
    email = TextField('Email Address', validators=[DataRequired(
        message='Enter your email address'), Email('Invalid Email')])
    password = PasswordField('Password', validators=[DataRequired(
        message='Enter a password.'), EqualTo('confirm')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(
        message="Type your password again.")])


class NewListForm(FlaskForm):
    """class to represent the new-list form"""
    list_name = StringField('Title', validators=[DataRequired(
        message='Enter a title for your shopping list')])


class NewItemForm(FlaskForm):
    """class to represent the new-item form"""
    item_name = TextField('Item Name', validators=[
        DataRequired('Enter a name for this item')])
    quantity = IntegerField('Quantity')
