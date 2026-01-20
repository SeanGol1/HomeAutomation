import json
import os
from flask import Blueprint, flash, render_template, request ,redirect, url_for
import website.functions as functions 

usersettings = Blueprint('usersettings', __name__)

staticTiles = ['weather-card','spotify-card', 'calendar-card' , 'general-controls-card' , 'website-controls-card', 
                  'clock-card', 'voice-card', 'maps-card' , 'system-card', 'scenes-card', ]



@usersettings.route('/', methods=['GET', 'POST'])
def settings():
    CONFIG_PATH = os.path.join(os.getcwd(), 'config.json')
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)


     # Load selected tiles from the config
    try:
        with open('configs/tiles.json') as f:
            tile_config = json.load(f)
        selected_tiles = tile_config.get('selected_tiles', [])
    except FileNotFoundError:
        selected_tiles = []

    if request.method == 'POST':
        try:
            # Top-level values
            config['weather']['weather_api_key'] = request.form.get('weather_api_key', config['weather']['weather_api_key'])
            config['weather']['city'] = request.form.get('city', config['weather']['city'])

            # Nested: Spotify
            config['spotify']['client_id'] = request.form.get('spotify_client_id', config['spotify']['client_id'])
            config['spotify']['client_secret'] = request.form.get('spotify_client_secret', config['spotify']['client_secret'])

            # Nested: Google
            if 'google' not in config:
                config['google'] = {}
            if 'maps_api_key' not in config['google']:
                config['google']['maps_api_key'] = ""
            config['google']['maps_api_key'] = request.form.get('maps_api_key', config['google']['maps_api_key'])
            if 'home_address' not in config['google']:
                config['google']['home_address'] = ""
            config['google']['home_address'] = request.form.get('home_address', config['google']['home_address'])


            # Nested: Firestick
            config['firestick']['adbclient_host'] = request.form.get('adbclient_host', config['firestick']['adbclient_host'])
            config['firestick']['adbclient_port'] = request.form.get('adbclient_port', config['firestick']['adbclient_port'])

            # Save updated config
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=4)
            flash("Settings updated successfully!", "success")
            return redirect(url_for('views.settings'))

        except Exception as e:
            flash(f"Error updating settings: {e}", "danger")

    # On GET, load current config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    return render_template('dashboardSettings.html', config=config , staticTiles = staticTiles, selected_tiles=selected_tiles, deviceList = functions.get_all_devices())


@usersettings.route('/save-tiles', methods=['POST'])
def save_tiles():
    selected_tiles = request.form.getlist('tiles[]')
    print("Selected tiles:", selected_tiles)

    if not selected_tiles:
        # fallback: collect everything with "tile-" prefix
        selected_tiles = [value for key, value in request.form.items() if key.startswith('tile-')]

    with open('configs/tiles.json', 'w') as f:
        json.dump({"selected_tiles": selected_tiles}, f, indent=2)

    # Save to session/database/config, etc.
    return redirect(url_for('views.dashboard'))

@usersettings.route('/addMapLocation/<address>', methods=['GET', 'POST'])
def addMapLocation(address):
    CONFIG_PATH = os.path.join(os.getcwd(), 'config.json')
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Ensure 'locations' exists and is a list
    if 'google' not in config:
        config['google'] = {}
    if 'locations' not in config['google'] or not isinstance(config['google']['locations'], list):
        config['google']['locations'] = []

    config['google']['locations'].append(address)

    # Save updated config
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    return f"Added address: {address}"

