from flask import Blueprint, request, jsonify ,redirect
from ..services.spotify_api import sp_oauth, get_current_track, send_control
from spotipy.oauth2 import SpotifyOAuth
import website.functions as functions 

spotify = Blueprint('spotify', __name__)


# Spotify
@spotify.route('/login_spotify')
def login_spotify():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@spotify.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        return "Authorization failed.", 400

    access_token = token_info['access_token']
    # Store token or use immediately to make an API call
    return "Spotify authorized successfully!"

@spotify.route('/spotify_status', methods=['GET','POST'])
def spotify_status():
    track = get_current_track()
    if track:
        return jsonify(track)
    return jsonify({"error": "No track playing or not authenticated."})

@spotify.route('/<action>', methods=['GET','POST'])
def spotify_control(action):
    print(action)
    result = send_control(action)

    if(result == "Success"):
        return jsonify({'status': f'Spotify {action} command sent'}), 200
    else:
        return "Error", 500
