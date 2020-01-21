from collections import defaultdict
import json
from functools import wraps
import datetime
from logging import getLogger

from flask import render_template, request, url_for,\
    redirect, flash, make_response, Blueprint

from app.content.models import BlogPost, RecentPosts, Likes
from app.views.wtforms import BlogForm
from factory_app import create_app
from models.exceptions import NotFound, ValidationError
from authentication import *

logger = getLogger(__name__)
recent_posts = RecentPosts()

app = create_app()


@app.route('/hello_world')
@login_required
def hello_world():
    return render_template('hello_world.html')


@app.route('/')
@app.route('/index')
@app.route('/welcome')
def welcome():
    print(request.user)
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
