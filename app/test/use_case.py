from flask import Flask, Blueprint

app = Flask(__name__)
app.register_blueprint('auth')