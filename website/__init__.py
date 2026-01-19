from flask import Flask
from os import path
from .views import views
from .routes.spotify import spotify
import json

def create_app():
    app= Flask(__name__)
    configdata = ''
    with open("config.json", "r") as jsonfile:
        configdata = json.load(jsonfile)
    app.secret_key = configdata["secretkey"]
    app.config['SESSION_COOKIE_SECURE'] = False  # Only for local dev (not production)
    app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(spotify,url_prefix='/spotify') 
    return app




