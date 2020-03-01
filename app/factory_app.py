from flask import Flask, render_template, request, url_for,\
    redirect, flash, make_response, Blueprint


def page_not_found(e):
    return render_template('404.html'), 404


def forbidden(e):
    return render_template('403.html'), 403


def unauthorized(e):
    return render_template('401.html'), 401


def unknown(e):
    return render_template('500.html'), 500


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = '7d8ed6dd-47e9-4fe6-bca5-ec62a721587e'
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(500, unknown)
    with app.app_context():
        from authentication import auth
        app.register_blueprint(auth)

    return app
