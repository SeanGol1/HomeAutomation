import spotipy, json
from spotipy.oauth2 import SpotifyOAuth

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

sp_oauth = SpotifyOAuth(
    client_id= configdata["spotify"]["client_id"],
    client_secret= configdata["spotify"]["client_secret"],
    redirect_uri="http://localhost:5000/spotify/callback",
    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
)

def get_spotify_client():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        return None
    return spotipy.Spotify(auth=token_info['access_token'])

def get_current_track():
    sp = get_spotify_client()
    if sp:
        return sp.current_playback()
    return None

def send_control(action):
    sp = get_spotify_client()
    if not sp:
        return "Error"

    try:
        current = sp.current_playback()

        if action == 'playpause':
            if current and current['is_playing']:
                sp.pause_playback()
            else:   #if current and not current['is_playing']:
                sp.start_playback()

        elif action == 'pause':
            sp.pause_playback()
        elif action == 'next':
            sp.next_track()
        elif action == 'previous':
            sp.previous_track()
        else:
            return "Error"

        return "Success"
    
    except Exception as e:
        return "Error"
