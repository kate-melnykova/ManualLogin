from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField, BooleanField, DateField
from wtforms.fields.html5 import EmailField
from wtforms import validators


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=15)])
    password = PasswordField('Password', [validators.Length(min=6, max=15)])
    rememberme = BooleanField('Remember me?')


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=15)])
    password = PasswordField('Password', [validators.Length(min=6, max=15)])
    confirm = PasswordField('Repeat Password',
                            [validators.InputRequired(),
                             validators.EqualTo('password', message='Passwords must match')])
    first_name = StringField('First name', [validators.Length(min=1, max=15)])
    dob = DateField('Date of birth in format Y-M-D', format='%Y-%m-%d')
    email = EmailField('Email', [validators.Length(min=6, max=50), validators.Email()])