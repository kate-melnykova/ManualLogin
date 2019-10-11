import datetime

from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response
import requests
from requests import Session, cookies
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField, BooleanField
from wtforms import validators

domain_address = 'http://127.0.0.1:5000'


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=6, max=35)])
    rememberme = BooleanField('Remember me?')


db = {
    'user': {'password':'password', 'first_name':'A'},
    'user2': {'password':'qwerty', 'first_name': 'B'}
    }


class AnonimousUser:
    pass


def is_logged_in(request):
    return request.cookies.get('username')


def auth(username, password, response):
    if username in db.keys():
        if db[username] == password:
            response.set_cookie('username', username)
            return True
        else:
            return False
    return False


app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route('/')
@app.route('/login')
def login():
    if is_logged_in(request):
        return redirect(url_for('logout'))
    else:
        loginform = LoginForm(request.form)
        return render_template('login.html', loginform=loginform, username=is_logged_in(request))


@app.route('/login/processing', methods=["POST"])
def login_processing():
    assert not is_logged_in(request)
    cookies_ = requests.get(domain_address).cookies
    print(f"Before request {cookies_}")
    loginform = LoginForm(request.form)
    if loginform.validate():
        username = loginform.username.data
        password = loginform.password.data
        r = make_response(redirect(url_for('logout')))
        if auth(username, password, r):
            if loginform.rememberme.data:
                r.set_cookie('is_logged_in', '1',
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))
            else:
                r.set_cookie('is_logged_in', '1')
            return r
        else:
            flash("Incorrect credentials")
            return redirect(url_for('login'))
    else:
        flash("Incorrect credentials")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if not is_logged_in(request):
        flash('You are not logged in')
        return redirect(url_for('login'))
    else:
        return render_template('logout.html', username=is_logged_in(request))


@app.route('/logout/confirmed', methods=["POST"])
def logout_process():
    assert is_logged_in(request)
    r = make_response(redirect(url_for('login')))
    r.delete_cookie('is_logged_in')
    r.delete_cookie('username')
    flash('Successfully logged out')
    return r


if __name__ == '__main__':
    app.run(debug=True)
