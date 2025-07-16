from flask import Flask
from os import path
from .views import views
import json

def create_app():
    app= Flask(__name__)
    configdata = ''
    with open("config.json", "r") as jsonfile:
        configdata = json.load(jsonfile)
    app.secret_key = configdata["secretkey"]
    app.register_blueprint(views, url_prefix='/')
    return app




