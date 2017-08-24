from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, Email
from wtforms import TextField, PasswordField

class LoginForm(FlaskForm):
    email = TextField('Email Address', validators=[InputRequired(message='Please enter an email address')])
    password = PasswordField('Enter Password', validators=[InputRequired('Please enter your password')])

class SignUpForm(FlaskForm):
    email = TextField('Email Address', validators=[InputRequired(message='Enter your email address'), Email('Invalid Email')])
    password = PasswordField('Password', validators=[InputRequired(message='Enter a password.'), EqualTo('confirm')])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(message="Type your password again.")])

class NewListForm(FlaskForm):
    list_name = TextField('Title', validators=[InputRequired(message='Enter a title for your new shopping list')])