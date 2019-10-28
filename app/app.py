import datetime
from functools import wraps

from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response, session
import requests
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField, BooleanField
from wtforms import validators

from app.auth import crypting
from app.auth.user_classes import *

domain_address = 'http://127.0.0.1:5000'

app = Flask(__name__)
app.secret_key = 'super secret key'


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=15)])
    password = PasswordField('Password', [validators.Length(min=6, max=15)])
    rememberme = BooleanField('Remember me?')


db = {
    'user': {'password':'password', 'first_name':'A'},
    'user2': {'password':'qwerty', 'first_name': 'B'}
    }


@app.before_request
def get_current_user():
    encrypted_username = request.cookies.get('username')

    if encrypted_username is None:
        request.user = AnonymousUser()
    else:
        try:
            username = crypting.aes_decrypt(encrypted_username)
        except Exception as ex:
            print(f"An exception of type {type(ex).__name__} occurred. Arguments:{ex.args}")
            request.user = AnonymousUser()
        else:
            if username in db:
                info = db[username]
                request.user = User(username, info)
            else:
                request.user = AnonymousUser()


def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not request.user.is_authenticated():
            r = make_response(redirect(url_for('login')))
            r.delete_cookie('username')
            r.delete_cookie('first_name')
            flash('You are not logged in')
            return r
        else:
            return func(*args, **kwargs)

    return wrapped


def auth(username, password, response):
    if username in db.keys():
        return db[username]['password'] == password
    return False


@app.route('/')
@app.route('/login')
def login():
    if not request.user.is_authenticated():
        login_form = LoginForm(request.form)
        return render_template(
            'login.html',
            loginform=login_form,
            user='AnonymousUser'
        )
    return redirect(url_for('logout'))


@app.route('/login/processing', methods=["POST"])
def login_processing():
    assert not request.user.is_authenticated()
    cookies_ = requests.get(domain_address).cookies
    print(f"Before request {cookies_}")
    loginform = LoginForm(request.form)
    if loginform.validate():
        username = loginform.username.data
        print('Retrieving username')
        password = loginform.password.data
        r = make_response(redirect(url_for('logout')))
        if auth(username, password, r):
            encrypted_username = crypting.aes_encrypt(username)
            first_name = db[username]['first_name']
            if loginform.rememberme.data:
                r.set_cookie('username', encrypted_username,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))
                r.set_cookie('first_name', first_name,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))

            else:
                r.set_cookie('username', encrypted_username)
                r.set_cookie('first_name', first_name)
            return r
        else:
            flash("Incorrect credentials")
            return redirect(url_for('login'))
    else:
        flash("Incorrect credentials")
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    print(f'On logout page, the current user is {request.user.username}')
    return render_template('logout.html',
                           user=request.user.first_name)


@app.route('/logout/confirmed', methods=["POST"])
@login_required
def logout_process():
    r = make_response(redirect(url_for('login')))
    r.delete_cookie('username')
    r.delete_cookie('first_name')
    flash('Successfully logged out')
    return r


@app.route('/hello_world')
@login_required
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
