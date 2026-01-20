from flask import Flask
from os import path

from .views import views
from .routes.spotify import spotify
from .routes.firestick import firestick
from .routes.google import google
from .routes.scenes import scenes
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
    app.register_blueprint(firestick,url_prefix='/firestick') 
    app.register_blueprint(google,url_prefix='/google') 
    app.register_blueprint(scenes,url_prefix='/scenes') 
    return app




