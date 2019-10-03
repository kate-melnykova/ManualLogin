from flask import Flask, render_template, request
import requests
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import validators


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=6, max=35)])


app = Flask(__name__)


@app.route('/login')
def login():
    loginform = LoginForm(request.form)
    return render_template('login.html', loginform=loginform)


if __name__ == '__main__':
    app.run()
