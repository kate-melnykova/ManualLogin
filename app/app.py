from functools import wraps
import datetime
from time import mktime

from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response, Blueprint

from app.auth import crypting
from app.auth.models import *
from app.views.wtforms import LoginForm, RegistrationForm


# app = Blueprint('auth', __name__)
app = Flask(__name__)
app.secret_key = '7d8ed6dd-47e9-4fe6-bca5-ec62a721587e'


@app.before_request
def get_current_user():
    encrypted_username = request.cookies.get('username')
    if encrypted_username is None:
        request.user = AnonymousUser()
    else:
        try:
            username = crypting.aes_decrypt(encrypted_username)
        except UnicodeDecodeError as ex:
            print(f"An exception of type {type(ex).__name__} occurred.")
            request.user = AnonymousUser()
        else:
            request.user = User.load(username)


def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            r = make_response(redirect(url_for('login')))
            r.delete_cookie('username')
            r.delete_cookie('first_name')
            flash('You are not logged in')
            return r
        else:
            return func(*args, **kwargs)

    return wrapped


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
    if request.user.is_authenticated():
        flash('You are already logged in!')
        return redirect(url_for('hello_world'))

    loginform = LoginForm(request.form)
    if loginform.validate():
        username = loginform.username.data
        password = loginform.password.data
        r = make_response(redirect(url_for('logout')))
        user = User.load(username)
        user.authenticate(password)
        if user.is_authenticated():
            encrypted_username = crypting.aes_encrypt(username)
            if loginform.rememberme.data:
                r.set_cookie('username', encrypted_username,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))
                r.set_cookie('first_name', user.first_name,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))

            else:
                r.set_cookie('username', encrypted_username)
                r.set_cookie('first_name', user.first_name)
            flash('You are successfully logged in')
            return r

    flash("Incorrect credentials")
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
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


@app.route('/registration')
def registration():
    regform = RegistrationForm()
    return render_template('registration.html',
                           regform=regform,
                           user=request.user.first_name)


@app.route('/registration/processing', methods=["POST"])
def registration_processing():
    form = RegistrationForm(request.form)
    if not form.validate():
        flash('Error')
        return redirect(url_for('registration'))

    username = form.username.data
    user = User.load(username)
    if isinstance(user, AnonymousUser):
        password = form.password.data
        first_name = form.first_name.data
        dob = mktime(form.dob.data.timetuple())
        email = form.email.data
        user = User(username, password, first_name,
                    dob, email)
        user.save()
        flash('Registration is successful! Please login.')
        return redirect(url_for('login'))
    else:
        flash('This username is not available')
        return redirect(url_for('registration'))


@app.route('/')
@app.route('/hello_world')
@login_required
def hello_world():
    return render_template('hello_world.html')


if __name__ == '__main__':
    app.run()
