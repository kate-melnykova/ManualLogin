import datetime

from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response
import requests
from requests import Session, cookies
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField, BooleanField
from wtforms import validators

from auth import crypting

domain_address = 'http://127.0.0.1:5000'


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=15)])
    password = PasswordField('Password', [validators.Length(min=6, max=15)])
    rememberme = BooleanField('Remember me?')


db = {
    'user': {'password':'password', 'first_name':'A'},
    'user2': {'password':'qwerty', 'first_name': 'B'}
    }


def get_current_user(request):
    encrypted_username = request.cookies.get('username')
    if encrypted_username is not None:
        try:
            username = crypting.aes_decrypt(encrypted_username)
        except Exception:
            return None
        if username in db.keys():
            return username
        else:
            return None
    else:
        return None


def auth(username, password, response):
    if username in db.keys():
        return db[username]['password'] == password
    return False


app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route('/')
@app.route('/login')
def login():
    if get_current_user(request) is not None:
        return redirect(url_for('logout'))
    else:
        loginform = LoginForm(request.form)
        return render_template('login.html',
                               loginform=loginform,
                               user="AnonymousUser")


@app.route('/login/processing', methods=["POST"])
def login_processing():
    assert get_current_user(request) is None
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
def logout():
    current_user = get_current_user(request)
    print(f'On logout page, the current user is {get_current_user(request)}')
    if current_user is None:
        flash('You are not logged in')
        return redirect(url_for('login'))
    else:
        first_name = db[current_user]['first_name']
        return render_template('logout.html',
                               user=first_name)


@app.route('/logout/confirmed', methods=["POST"])
def logout_process():
    assert get_current_user(request) is not None
    r = make_response(redirect(url_for('login')))
    r.delete_cookie('username')
    r.delete_cookie('first_name')
    flash('Successfully logged out')
    return r


if __name__ == '__main__':
    app.run(debug=True)
