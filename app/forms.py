"""module for shoppinglist-api forms"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, TextField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User


class ExistingUser(object):
    """class to validate if a given email exists in the database
    """

    def __init__(self, message=""):
        self.message = message

    def __call__(self, form, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError(self.message)
#consider using another form of validation. This one seems to be glitchy.

class LoginForm(FlaskForm):
    """class to represent the login form"""
    email = TextField('Email Address', validators=[
        DataRequired(message='Please enter an email address'),
        Email()])
    password = PasswordField('Enter Password', validators=[
        DataRequired('Please enter your password')])


class SignUpForm(FlaskForm):
    """class to represent the sign-up form"""
    email = TextField('Email Address', validators=[
        DataRequired(message='Enter your email address.'),
        Email()])
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


class ForgotPasswordForm(FlaskForm):
    """class to represent the form password reset form. Takes the User's email ID"""
    email = TextField('Email Address', validators=[
        DataRequired(message='Enter your email address.'),
        Email(), ExistingUser()])


class ResetPasswordForm(FlaskForm):
    """class to represent the password reset form. Takes User's new password."""
    new_password = PasswordField('Enter New Password',
                                 validators=[DataRequired(message='Please enter a password.'),
                                             EqualTo('confirm')])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired('Please re-enter the password')])
