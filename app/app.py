from functools import wraps
import datetime
from time import mktime

from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response, Blueprint

from app.models.basemodel import NotFound
from app.auth import crypting
from app.auth.models import User, AnonymousUser
from app.content.models import BlogPost, RecentPosts
from app.views.wtforms import LoginForm, RegistrationForm, BlogForm


def page_not_found(e):
    return render_template('404.html'), 404


def forbidden(e):
    return render_template('403.html'), 403


def unauthorized(e):
    return render_template('401.html'), 401


recent_posts = RecentPosts()

app = Flask(__name__)
app.secret_key = '7d8ed6dd-47e9-4fe6-bca5-ec62a721587e'
app.register_error_handler(404, page_not_found)
app.register_error_handler(403, forbidden)
app.register_error_handler(401, unauthorized)


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
            print('Loading user based on cookies')
            try:
                request.user = User.load(username)
            except NotFound:
                request.user = AnonymousUser()


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


@app.context_processor
def inject_user():
    return dict(user=request.user)


@app.route('/login')
def login():
    if not request.user.is_authenticated:
        login_form = LoginForm(request.form)
        return render_template(
            'login.html',
            loginform=login_form
        )
    return redirect(url_for('logout'))


@app.route('/login/processing', methods=["POST"])
def login_processing():
    if request.user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('hello_world'))

    loginform = LoginForm(request.form)
    if loginform.validate():
        username = loginform.username.data
        password = loginform.password.data
        r = make_response(redirect(url_for('hello_world')))
        try:
            user = User.load(username)
        except NotFound:
            flash("Incorrect credentials: please double-check username")
            return redirect(url_for('login'))

        print(f'Login: user password is {user.password}')
        print(f'Login: password entered is {password}')
        print(f'Login: loaded user is an object of class {type(user)}')
        if user.verify_password(password):
            encrypted_username = crypting.aes_encrypt(username)
            if loginform.rememberme.data:
                r.set_cookie('username', encrypted_username,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))
                r.set_cookie('first_name', user.first_name,
                             expires=datetime.datetime.now() + datetime.timedelta(days=365))

            else:
                r.set_cookie('username', encrypted_username)
                r.set_cookie('first_name', user.first_name)
            flash('You are successfully logged in!')
            return r
        else:
            flash("Incorrect credentials: please double-check username and password")
            return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    return render_template('logout.html')


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
    if request.user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('hello_world'))

    regform = RegistrationForm()
    return render_template('registration.html',
                           regform=regform)


@app.route('/registration/processing', methods=["POST"])
def registration_processing():
    form = RegistrationForm(request.form)
    if not form.validate():
        flash('Error: incorrect entry in the form')
        return redirect(url_for('registration'))

    username = form.username.data
    print('Registration user loading')
    try:
        user = User.load(username)
    except NotFound:
        pass
    else:
        flash('This username is not available')
        return redirect(url_for('registration'))

    password = form.password.data
    first_name = form.first_name.data
    dob = form.dob.data.timetuple()
    email = form.email.data
    User.create(username=username, password=password,
                first_name=first_name, dob=dob,
                email=email)
    flash('Registration is successful! Please login.')
    return redirect(url_for('login'))


@app.route('/hello_world')
@login_required
def hello_world():
    return render_template('hello_world.html')


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@login_required
@app.route('/blogpost_edit')
def blogpost_edit():
    print('I am here')
    return render_template('blogpost_editor.html', blogform=BlogForm())


@login_required
@app.route('/blogpost/create', methods=['POST'])
def blogpost_create():
    form = BlogForm(request.form)
    if not form.validate():
        flash('Error: incorrect entry in the form')
        return redirect(url_for('blogpost_edit'))

    author = request.user.username
    author_id = request.user.id
    # id = form.id
    title = form.title.data
    content = form.content.data

    blogpost = BlogPost.create(author=author, author_id=author_id,
                               title=title, content=content)
    recent_posts.add(blogpost.id)
    flash('Blogpost is successfully created')
    return redirect(url_for('welcome'))


@app.route('/blogpost_recent')
def blogpost_recent():
    posts = [BlogPost.load(post_id) for post_id in recent_posts.post_ids]
    return render_template('blogpost_recent.html', posts=posts)


@login_required
@app.route('/account')
def account():
    user = request.user
    posts = BlogPost.search(author=user.username)
    return render_template('account.html', user=user, posts=posts)


@app.route('/profile')
def profile():
    view_user = request.args.get('username')
    try:
        view_user = User.load(view_user)
    except:
        flash(f'Username {view_user} does not exist')
        return redirect(url_for('blogpost_recent'))
    else:
        view_user = view_user.username
        posts = BlogPost.search(author=view_user)

    return render_template('profile.html', username=view_user, posts=posts)


if __name__ == '__main__':
    app.run()
