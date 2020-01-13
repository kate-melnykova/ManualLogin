from collections import defaultdict
import json
from functools import wraps
import datetime
from logging import getLogger

from flask import render_template, request, url_for,\
    redirect, flash, make_response

from app.auth import crypting
from app.auth.models import User, AnonymousUser
from app.content.models import BlogPost, RecentPosts, Likes
from app.views.wtforms import LoginForm, RegistrationForm, BlogForm, UpdateUserForm
from factory_app import create_app
from models.exceptions import NotFound, ValidationError

logger = getLogger(__name__)
recent_posts = RecentPosts()

app = create_app()


@app.before_request
def get_current_user():
    encrypted_username = request.cookies.get('username')
    if encrypted_username is None:
        request.user = AnonymousUser()
    else:
        try:
            username = crypting.aes_decrypt(encrypted_username)
        except UnicodeDecodeError:
            request.user = AnonymousUser()
        else:
            try:
                request.user = User.load(username)
            except NotFound:
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


@app.context_processor
def inject_user():
    return dict(user=request.user)


@app.route('/login')
def login():
    form_error = request.cookies.get('form_error')
    try:
        form_error = json.load(form_error)
    except TypeError:
        form_error = defaultdict(str)
    except AttributeError:
        form_error = defaultdict(str)
    if not request.user.is_authenticated():
        login_form = LoginForm(request.form)
        return render_template('login.html', loginform=login_form)
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
        r = make_response(redirect(url_for('hello_world')))
        try:
            user = User.load(username)
        except NotFound:
            logger.info(f'user {username} is not found')
            r = make_response(redirect(url_for('login')))
            flash("Incorrect credentials: please double-check username")
            return r

        logger.info(f'Login: user password is {user.password}')
        logger.info(f'Login: password entered is {password}')
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
            r.set_cookie('form_error', json.dumps(loginform.errors))
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


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        form_error = request.cookies.get('form_error')
        try:
            form_error = json.loads(form_error)
        except TypeError or AttributeError:
            form_error = dict()

        if request.user.is_authenticated():
            r = make_response(redirect(url_for('hello_world')))
            r.delete_cookie('form_error')
            flash('You are already logged in!')
            return r

        regform = RegistrationForm()
        for attr in regform.get_attributes():
            getattr(regform, attr).saved_error = form_error.get(attr, [])
        r = make_response(render_template('registration.html', regform=regform))
        r.delete_cookie('form_error')
        return r


@app.route('/registration/processing', methods=["POST"])
def registration_processing():
    form = RegistrationForm(request.form)
    if not form.validate():
        flash('Error: incorrect entry in the form')
        r = make_response(redirect(url_for('registration')))
        r.set_cookie('form_error', json.dumps(form.errors))
        return r

    username = form.username.data
    if not User.exists(username):
        password = form.password.data
        first_name = form.first_name.data
        dob = form.dob.data
        email = form.email.data
        User.create(username=username, password=password,
                    first_name=first_name, dob=dob,
                    email=email)
        flash('Registration is successful! Please login.')
        return redirect(url_for('login'))

    else:
        flash('This username is not available')
        return redirect(url_for('registration'))


@app.route('/update_user')
@login_required
def update_user():
    form_error = request.cookies.get('form_error')
    try:
        form_error = json.loads(form_error)
    except TypeError or AttributeError:
        form_error = dict()

    form = UpdateUserForm()
    for attr in form.get_attributes():
        if attr in request.user.get_attributes():
            cur_value = getattr(request.user, attr)
            if cur_value != getattr(User, attr).default:
                getattr(form, attr).data = cur_value

    for attr in form.get_attributes():
        getattr(form, attr).saved_error = form_error.get(attr, [])
    r = make_response(render_template('update_user.html', form=form))
    r.delete_cookie('form_error')
    return r


@app.route('/update_user/processing', methods=['POST'])
@login_required
def update_user_processing():
    form = UpdateUserForm(request.form)
    if not form.validate():
        flash('Error: incorrect entry in the form')
        r = make_response(redirect(url_for('update_user')))
        r.set_cookie('form_error', json.dumps(form.errors))
        return r

    print(f'Data is {form.data}')
    print(f'Entered username is {form.username.data}')
    print(f'Entered password is {form.cur_password.data}')
    if request.user.verify_password(form.cur_password.data):
        data = dict()
        for attr in form.get_attributes():
            data[attr] = getattr(form, attr).data
        request.user.update(**data)

        encrypted_username = crypting.aes_encrypt(form.username.data)
        r = make_response(redirect(url_for('blogpost_recent')))
        r.set_cookie('username', encrypted_username)
        r.set_cookie('first_name', form.first_name.data)
        flash('You are successfully logged in!')
        return r
    else:
        flash("Incorrect credentials: please double-check password")
        return redirect(url_for('update_user'))


@app.route('/hello_world')
@login_required
def hello_world():
    return render_template('hello_world.html')


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/blogpost_edit')
@login_required
def blogpost_edit():
    return render_template('blogpost_editor.html', blogform=BlogForm())


@app.route('/blogpost/create', methods=['POST'])
@login_required
def blogpost_create():
    if not request.user.is_authenticated():
        flash('You are not logged in')
        return redirect(url_for('login'))

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
    posts = list(BlogPost.load(post_id) for post_id in recent_posts.posts)
    for idx, post in enumerate(posts):
        like_count = 0
        user_like = False
        for like in Likes.search(blogpost_id=post.id):
            like_count += 1
            if request.user.is_authenticated() and like.user_id == request.user.id \
                    and like.blogpost_id == post.id:
                user_like = True
        posts[idx] = (post, like_count, user_like)
    return render_template('blogpost_recent.html', posts=posts)


@app.route('/account')
@login_required
def account():
    sorting = request.args.get('sort')
    posts = list(BlogPost.search(author=request.user.username))
    n_likes = 0
    for idx, post in enumerate(posts):
        posts[idx] = (post,
                      len(Likes.search(blogpost_id=post.id)),
                      bool(Likes.exists(Likes._generate_id(blogpost_id=post.id, user_id=request.user.id))))
        n_likes += posts[idx][1]
    if sorting == 'date':
        posts = sorted(posts, key=lambda post: post[0].date, reverse=True)
    else:
        posts = sorted(posts, key=lambda post: post[1], reverse=True)
    request.user.likes = n_likes
    return render_template('account.html', posts=posts)


@app.route('/profile')
def profile():
    view_user = request.args.get('username')
    try:
        view_user = User.load(view_user)
    except NotFound:
        flash(f'Username {view_user} does not exist')
        return redirect(url_for('blogpost_recent'))
    else:
        view_user = view_user.username
        posts = BlogPost.search(author=view_user)

    return render_template('profile.html', username=view_user, posts=posts)


@app.route('/like_post')
@login_required
def like_post():
    like_id = request.args.get('like_id')
    type, user_id, blogpost_id = like_id.split('_')
    if user_id != request.user.id:
        return redirect(url_for('blogpost_recent'))

    if type == 'like':
        Likes.create(user_id=user_id, blogpost_id=blogpost_id)
    elif type == 'unlike':
        Likes.delete(Likes.info_to_db_key(user_id=user_id, blogpost_id=blogpost_id))
    else:
        print(f'Actual type is {type}')
        logger.info(f'Trying to create like/unlike with unverfified command {type}')
    return redirect(url_for('blogpost_recent'))


if __name__ == '__main__':
    app.run()
