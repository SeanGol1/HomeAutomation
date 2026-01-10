#from distutils.command.config import config
#from multiprocessing.connection import wait
# from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify ,  make_response, redirect,url_for, session
from . import fireStickController
import json , time , tinytuya ,  numpy as np , requests , speedtest, psutil , spotipy, subprocess, os, platform #cv2,
from .spotify_api import sp_oauth, get_current_track, send_control
from spotipy.oauth2 import SpotifyOAuth
from ppadb.client import Client as AdbClient #pip install pure-python-adb
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import website.functions as functions 

views = Blueprint('views', __name__)

spotify = Blueprint('spotify', __name__)

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

views.secret_key = configdata["secretkey"] 
# views.config['SESSION_COOKIE_SECURE'] = False  # For local dev only
# views.config['SESSION_COOKIE_SAMESITE'] = "Lax"

class Device:
  def __init__(self, name, ip, type,make,id,key,version,room):
    self.name = name
    self.ip = ip
    self.type = type
    self.make = make
    self.id = id 
    self.key = key
    self.version = version
    self.room = room

class Bulb(Device):
    def __init__(self,name, ip, type,make,id,key,version,room,state, brightness, colour):
        Device.__init__(self, name, ip, type,make,id,key,version,room)
        self.state = state
        self.brightness = brightness
        self.colour = colour

staticTiles = ['weather-card','spotify-card', 'calendar-card' , 'general-controls-card' , 'website-controls-card', 
                  'clock-card', 'voice-card', 'maps-card' , 'system-card', 'scenes-card', ]

### WEBSITE ROUTES ###
@views.route('/')
def home():    
    return render_template("home.html")

@views.route('/devices', methods=['GET','POST'])
def devices():
    return render_template("devices.html",deviceList=functions.get_all_device_objs())

@views.route('/addDevice', methods=['GET'])
def addDevice():
    return render_template("addDevice.html")

@views.route('/addDevice', methods=['POST'])
def addDevicePost():
    #Add device to config file.
    new_device = {
        "name": request.form.get("device_name"),
        "ip": request.form.get("device_ip"),
        "type": request.form.get("device_type"),
    }

    # Add light-specific fields if it's a smart bulb
    if new_device["type"] == "light":
        new_device.update({
            "make": request.form.get("device_make"),
            "id": request.form.get("device_id"),
            "key": request.form.get("device_key")
        })

    # # Load existing config
    try:
        with open("config.json", 'r') as f:
            configdata = json.load(f)
    except FileNotFoundError:
            configdata = {"devices": []}

    # Add the new device
    configdata["devices"].append(new_device)

    # Save back to file
    with open("config.json", 'w') as f:
        json.dump(configdata, f, indent=4)

    return redirect("/devices", code=200)


@views.route('/deleteDevice', methods=['POST'])
def delete_device():
    data = request.get_json()
    ip = data.get('ip')

    try:
        with open("config.json", 'r') as f:
            configdata = json.load(f)

        configdata['devices'] = [d for d in configdata['devices'] if d.get('ip') != ip]

        with open("config.json", 'w') as f:
            json.dump(configdata, f, indent=4)

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting device: {e}")
        return jsonify({"success": False})

@views.route('/dashboard', methods=['GET','POST'])
def dashboard():

    with open("config.json", 'r') as f:
        configdata = json.load(f)

    maps_api_key = configdata["google"]["maps_api_key"]
    # Load selected tiles from the config
    try:
        with open('tiles.json') as t:
            tile_config = json.load(t)
        selected_tiles = tile_config.get('selected_tiles', [])
    except FileNotFoundError:
        selected_tiles = []

    sp_oauth = SpotifyOAuth(
        client_id= configdata["spotify"]["client_id"],
        client_secret= configdata["spotify"]["client_secret"],
        redirect_uri="http://localhost:5000/spotify/callback",
        scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
    )
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        return redirect('/spotify/login_spotify')  # No token? Login first.

    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_track = sp.current_playback()


    api_key = configdata['weather']['weather_api_key']
    location = configdata['weather']['city']  
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=5&aqi=no&alerts=no"
    
    weather_data = {}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            for day in weather_data['forecast']['forecastday']:
                date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
                day['weekday'] = date_obj.strftime('%a')
    except Exception as e:
        print("Error fetching weather:", e)

    return render_template("dashboard.html", deviceList=functions.get_all_device_objs(), weather=weather_data,maps_api_key=maps_api_key, selected_tiles=selected_tiles, scenes=functions.get_all_scenes())


@views.route('/devicesDashboard', methods=['GET','POST'])
def dashboardDevices():
    return render_template("dashboardDevices.html",deviceList=functions.get_all_device_objs())


@views.route('/system_status')
def system_status():
    # CPU and RAM usage
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    # Network speed test
    try:
        st = speedtest.Speedtest()
        download = round(st.download() / 1_000_000, 2)  # Mbps
        upload = round(st.upload() / 1_000_000, 2)      # Mbps
    except:
        download = upload = None

    return jsonify({
        'cpu': cpu,
        'ram': ram,
        'download': download,
        'upload': upload
    })

@views.route('/get_device_status')
def get_device_status():
    deviceList = functions.get_all_device_objs()
    devices = []
    for d in deviceList:
        devices.append({
            'name': d.name,
            'ip': d.ip,
            'type': d.type,
            'state': d.state if hasattr(d, 'state') else None,
            'brightness': d.brightness if hasattr(d, 'brightness') else None,
            'colour': d.colour if hasattr(d, 'colour') else None,
        })
    return jsonify(devices)




### Settings

@views.route('/settings', methods=['GET', 'POST'])
def settings():
    CONFIG_PATH = os.path.join(os.getcwd(), 'config.json')
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)


     # Load selected tiles from the config
    try:
        with open('tiles.json') as f:
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


@views.route('/save-tiles', methods=['POST'])
def save_tiles():
    selected_tiles = request.form.getlist('tiles[]')
    print("Selected tiles:", selected_tiles)

    if not selected_tiles:
        # fallback: collect everything with "tile-" prefix
        selected_tiles = [value for key, value in request.form.items() if key.startswith('tile-')]

    with open('tiles.json', 'w') as f:
        json.dump({"selected_tiles": selected_tiles}, f, indent=2)

    # Save to session/database/config, etc.
    return redirect(url_for('views.dashboard'))

@views.route('/addMapLocation/<address>', methods=['GET', 'POST'])
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



### Scenes

@views.route('/addScene', methods=['POST'])
def add_scene():
    try:
        # Get the posted data
        data = request.get_json()
        steps = data.get('steps', [])
        name = data.get('name','')

        # If scenes.config doesn't exist yet, start with empty dict
        if not os.path.exists('scenes.json'):
            scenes_data = {}
        else:
            with open('scenes.json', 'r') as f:
                try:
                    scenes_data = json.load(f)
                except json.JSONDecodeError:
                    scenes_data = {}

        # Generate a new scene name (you can enhance this later to accept custom names)
        scene_name = f"{name}"
        scenes_data[scene_name] = steps

        # Write updated data back to file
        with open('scenes.json', 'w') as f:
            json.dump(scenes_data, f, indent=2)

        return jsonify({ "status": "success", "scene": scene_name }), 200

    except Exception as e:
        print(f"Error saving scene: {e}")
        return jsonify({ "status": "error", "message": str(e) }), 500

@views.route('/deleteScene/<scene_name>', methods=['POST'])
def delete_scene(scene_name):
    if not os.path.exists('scenes.json'):
        return False, "Scene file not found."

    with open('scenes.json', 'r') as f:
        scenes = json.load(f)

    if scene_name not in scenes:
        return False, "Scene not found."

    del scenes[scene_name]

    with open('scenes.json', 'w') as f:
        json.dump(scenes, f, indent=2)

    return jsonify({ "status": "success", "scene": scene_name }), 200

@views.route('/scenes', methods=['GET', 'POST'])
def create_scene():
    # with open('config.json') as f:
    #     config = json.load(f)
    # device_list = config.get("devices", []) 
    device_list = functions.get_all_devices()
    scenes = functions.get_all_scenes_names()

    if request.method == 'POST':
        scene_name = request.form.get('scene_name')
        devices = []

        # Collect all posted devices data
        for key in request.form:
            if key.startswith('devices['):
                parts = key.split('][')
                index = parts[0][8:]  # devices[0
                field = parts[1][:-1]  # remove trailing ]

                while len(devices) <= int(index):
                    devices.append({})

                devices[int(index)][field] = request.form.get(key)

        # Filter out devices with "none" action
        scene_devices = [d for d in devices if d.get('action') != 'none']

        if scene_devices:
            # Load existing scenes
            scenes_path = 'scenes.json'
            scenes = []
            if os.path.exists(scenes_path):
                with open(scenes_path, 'r') as f:
                    scenes = json.load(f)

            # Add new scene
            new_scene = {
                "name": scene_name,
                "devices": scene_devices
            }
            scenes.append(new_scene)

            with open(scenes_path, 'w') as f:
                json.dump(scenes, f, indent=4)

        return redirect(url_for('views.dashboard'))

    return render_template('dashboardScenes.html', deviceList=device_list, scenes=scenes)

def send_device_command(ip, action, option):

    if(action == 'state'):
        lampswitch_int(ip,option)
    elif(action == 'brightness'):
        setlampbright_int(ip,option)
    elif(action == 'colour'):
        setcolour_int(ip,option)
    

@views.route('/run_scene/<scene_name>', methods=['POST'])
def run_scene(scene_name):
    try:
        with open('scenes.json') as f:
            sceneconfig = json.load(f)

        steps = sceneconfig.get(scene_name)
        if not steps:
            return jsonify({"error": "Scene not found"}), 404

        results = []
        # Define action priority
        priority = {"state": 0, "colour": 1, "brightness": 2}

        # Sort steps based on priority
        steps.sort(key=lambda s: priority.get(s["action"], 99))
        
        for step in steps:
            success = send_device_command(step['device'], step['action'], step['option'])
            results.append({
                "device": step["device"],
                "action": step["action"],
                "option": step["option"],
                "status": "success" if success else "failed"
            })

        return jsonify({"scene": scene_name, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

####




@views.route("/remote/<ip>", methods=["GET", "POST"])
def remote(ip):
    if request.method == "POST":
        action = request.form.get("action")
        device = get_device(ip)
        if device and action:
            send_key(device, action)
    return render_template("remote.html")

KEYS = {
    "up": 19,
    "down": 20,
    "left": 21,
    "right": 22,
    "ok": 23,
    "back": 4,
    "home": 3,
    "menu": 82,
    "play_pause": 85,
    "rewind": 89,
    "fast_forward": 90,
    "power": 26,
}

def get_device(ip):
    config = ''
    with open("config.json", "r") as jsonfile:
        config = json.load(jsonfile)
    finalip = ip + ':5555'
    try:
        client = AdbClient(host=config["firestick"]["adbclient_host"], port=int(config["firestick"]["adbclient_port"]))
        device = client.device(finalip)
        if not device:
            functions.connect_to_firestick(ip)
    except:
        functions.connect_to_firestick(ip)
    finally: 
        if not client:
            client = AdbClient(host=config["firestick"]["adbclient_host"], port=int(config["firestick"]["adbclient_port"]))  
        if not device:
            device = client.device(finalip)
    
    return device

def send_key(device, key_name):
    keycode = KEYS.get(key_name.lower())
    if keycode:
        device.shell(f"input keyevent {keycode}")

@views.route("/voice", methods=["GET", "POST"])
def voice():
    if request.method == "GET":
        return render_template("voice.html")
    
    if request.method == "POST":
        #devices = get_all_devices()
        data = request.get_json()
        text = data.get("text", "")
        response_text = ""
        if "weather" in text:
            response_text = "Look out the window, you lazy bastard!"

        if "joke" in text:
            response_text = "Turning on the camera so you can see yourself!"

        result = functions.getAction(text)

        return jsonify({"response": response_text})


### Control Devices Endpoints ###

@views.route('/lampswitch/<ip>', methods=['POST'])
def lampswitch(ip):
    d,data = functions.tinytuya_connect(ip)
    isOn = False
    if data['dps']['20'] == False:
        d.turn_on()
        isOn = True
    else:
        d.turn_off()
        isOn = False
    print(jsonify(isOn))


    response = make_response(jsonify({'isOn': isOn}), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def lampswitch_int(ip,on):
    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,'Auto',device.key)
    d.set_version(device.version) 

    isOn = False
    if on == True:
        d.turn_on()
        isOn = True
    else:
        d.turn_off()
        isOn = False
    print(jsonify(isOn))

    response = make_response("Success", 200)
    response.headers['Content-Type'] = 'application/json'
    return response


# /lampbright/<ip> - Toggles brightness between 25 , 100 , 255
@views.route('/lampbright/<ip>', methods=['GET','POST'])
def lampbright(ip):
    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,'Auto',device.key)
    d.set_version(device.version)  
    
    data = d.status()
    d.turn_on()
    if data['dps']['21'] == 'colour':
        brightness = functions.get_brightness_from_hex(data["dps"]["24"])
        if brightness > 67:
            d.set_brightness_percentage(25)
        elif brightness < 67 and brightness > 26:
            d.set_brightness_percentage(100)
        else:
            d.set_brightness_percentage(66)
    elif data['dps']['21'] == 'white':
        if data['dps']['22'] == 255:
            d.set_brightness(25)
        elif data['dps']['22'] == 25:
            d.set_brightness(100)
        else:
            d.set_brightness(255)
    data = d.status()
    #print(data)
    return "Success"

# /lampbright/{ip,brightness} - sets brightness to to a percentage value. 
@views.route('/setlampbright', methods=['GET','POST'])
def setlampbright(data):
    data = request.get_json()
    ip = data['ip']
    brightness = data['brightness']

    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(device.version)  
    
    data = d.status()    
    d.turn_on()
    
    #print(int(brightness))
    if(int(brightness) == 0):
        d.turn_off()
    else:
        d.set_brightness_percentage(int(brightness))

    data = d.status()
    #print(data)
    
    return "Success"


def setlampbright_int(ip,brightness):
    # data = request.get_json()
    # ip = data['ip']
    # brightness = data['brightness']

    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(device.version)  
    
    data = d.status()    
    d.turn_on()
    
    #print(int(brightness))
    if(int(brightness) == 0):
        d.turn_off()
    else:
        d.set_brightness_percentage(int(brightness))

    data = d.status()
    #print(data)
    
    return "Success"



# /lampbright/{ip,colour(hex)} - Sets colour of the light
@views.route('/setcolour', methods=['GET','POST'])
def setcolour():
    data = request.get_json()
    ip = data['ip']
    colour = data['colour']

    device:Device = functions.get_device_by_ip(ip)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(device.version)      
    data = d.status()
    d.turn_on()

    colour = colour[1:]
    c = functions.hex_to_rgb(colour)
    if (colour.lower() == 'ffffff'):
        d.set_white(1000,10)
    else:
        c = functions.hex_to_rgb(colour)
        d.set_colour(c[0],c[1],c[2])

    return "Success"

# /lampbright/{ip,colour(hex)} - Sets colour of the light
def setcolour_int(ip,colour):
    device:Device = functions.get_device_by_ip(ip)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(device.version)      
    data = d.status()
    d.turn_on()

    colour = colour[1:]
    c = functions.hex_to_rgb(colour)
    if (colour.lower() == 'ffffff'):
        d.set_white(1000,10)
    else:
        c = functions.hex_to_rgb(colour)
        d.set_colour(c[0],c[1],c[2])

    return "Success"

@views.route('/lightsoff', methods=['GET','POST'])
def lightsoff():
    #Light
    deviceList= functions.get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            b.set_version(d.version)
            b.turn_off()

@views.route('/lightson', methods=['GET','POST'])
def lightson():
    #Light
    deviceList= functions.get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            b.set_version(d.version)
            b.turn_on()

### Control Firestick ###

@views.route('/next_episode', methods=['GET','POST'])
def next_episode():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.down()
    mc.down()
    mc.right()
    mc.right()
    mc.right()
    mc.select()
    time.sleep(5)
    mc.up()
    mc.right()
    mc.select()

@views.route('/recent_show', methods=['GET','POST'])
def recent_show():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.home()
    mc.right()
    mc.right()
    mc.right()
    mc.select()
    time.sleep(5)
    mc.right()
    mc.right()
    mc.select()
    mc.up()
    mc.up()
    mc.select()
    mc.right()
    mc.up()
    mc.select()

@views.route('/playpause', methods=['GET','POST'])
def playpause():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    
    mc.addDevice(fireStickIP)
    mc.playpause()
    
@views.route('/poweroff', methods=['GET','POST'])
def powerdown():
    fireStickIP = configdata['firestick_IP']
    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.poweroff()

@views.route('/formula1', methods=['GET','POST'])
def f1():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.home()
    time.sleep(1)
    mc.right(), mc.right(), mc.right()
    mc.select()
    time.sleep(10)
    mc.select()
    time.sleep(3)
    mc.left(), mc.down(), mc.down()
    mc.select()
    mc.down(), mc.down(), mc.down(), mc.down(), mc.down(), mc.down(), mc.down(), mc.down()
    mc.select(), mc.select()

@views.route('/wakeup', methods=['GET','POST'])
def wakeup():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.home()
    
    
### Change lights to match the colour that the camera picks up ###
# @views.route('/moodlight', methods=['GET','POST'])
# def moodlight():
#     # taking the input from webcam
#     vid = cv2.VideoCapture(0)

#     d = tinytuya.BulbDevice(configdata['Light_ID_1'], configdata['Light_IP_1'], configdata['Light_KEY_1'])
#     d.set_version(3.1)  # IMPORTANT to set this regardless of version
#     d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

  
#     # running while loop just to make sure that
#     # our program keep running until we stop it
#     while True:
        

#         # capturing the current frame
#         _, frame = vid.read()

#         # displaying the current frame
#         cv2.imshow("frame", frame)

#         # setting values for base colors
#         b = frame[:, :, :1]
#         g = frame[:, :, 1:2]
#         r = frame[:, :, 2:]

#         # computing the mean
#         b_mean = np.mean(b)
#         g_mean = np.mean(g)
#         r_mean = np.mean(r)

#         #d.set_brightness(255)
          
#         # # Set to RED Color - set_colour(r, g, b):
#         d.set_colour(r_mean,g_mean,b_mean)
#         #if(r>255):
#          #   r = 255
#         #if(g>255):
#         #   g = 255
#         #if(b>255):
#          #   b=255
            
#         #d.set_colour(r,g,b)
#         data = d.status()
#         #print('r'+str(r),'g'+str(g), 'b'+ str(b))
#         print('R'+str(r_mean),'G'+str(g_mean),'B'+str(b_mean))
#         #print('set_status() result %r' % data)

# Spotify
@views.route('/spotify/login_spotify')
def login_spotify():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@views.route('/spotify/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        return "Authorization failed.", 400

    access_token = token_info['access_token']
    # Store token or use immediately to make an API call
    return "Spotify authorized successfully!"

@views.route('/spotify/spotify_status', methods=['GET','POST'])
def spotify_status():
    track = get_current_track()
    if track:
        return jsonify(track)
    return jsonify({"error": "No track playing or not authenticated."})

@views.route('/spotify/<action>', methods=['GET','POST'])
def spotify_control(action):
    print(action)
    result = send_control(action)

    if(result == "Success"):
        return jsonify({'status': f'Spotify {action} command sent'}), 200
    else:
        return "Error", 500

# Google

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "google.json"

@views.route('/authorize' , methods=['GET','POST'])
def authorize():
    # redirect_uri = url_for('views.oauth2callback', _external=True)
    redirect_uri = 'https://415d19f830e7.ngrok-free.app/google/callback'
    print("🚀 Redirect URI being used:", redirect_uri)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri)
    
    # auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    auth_url, state = flow.authorization_url() 
    #        access_type='offline',
        #include_granted_scopes='true'

    session['state'] = state
    

    return redirect(auth_url)

@views.route('google/callback', methods=['GET','POST'])
def oauth2callback():
    redirect_uri = 'https://415d19f830e7.ngrok-free.app/google/callback'

    # state = session['state']
    # if not state: 
    #     return "Error"

    # print( 'State: ' + state)   
    
    # Rebuild the flow with the same state
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        # state=state,
        redirect_uri=redirect_uri
    )

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    # Save the credentials and device info in the session or database
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect('/calendar')

@views.route('/calendar', methods=['GET','POST'])
def calendar():
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return render_template('calendar.html', events=events)

