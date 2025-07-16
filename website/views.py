#from distutils.command.config import config
from multiprocessing.connection import wait
from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify ,  make_response, redirect,url_for, session
from . import fireStickController
import json , time , tinytuya , cv2, numpy as np , requests , speedtest, psutil , spotipy, subprocess, os, platform
from .spotify_api import sp_oauth, get_current_track
from spotipy.oauth2 import SpotifyOAuth
from ppadb.client import Client as AdbClient #pip install pure-python-adb
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

views = Blueprint('views', __name__)

spotify = Blueprint('spotify', __name__)

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

views.secret_key = configdata["secretkey"] 

class Device:
  def __init__(self, name, ip, type,make,id,key):
    self.name = name
    self.ip = ip
    self.type = type
    self.make = make
    self.id = id 
    self.key = key

class Bulb(Device):
    def __init__(self,name, ip, type,make,id,key,state, brightness, colour):
        Device.__init__(self, name, ip, type,make,id,key)
        self.state = state
        self.brightness = brightness
        self.colour = colour

### WEBSITE ROUTES ###
@views.route('/')
def home():    
    return render_template("home.html")

@views.route('/devices', methods=['GET','POST'])
def devices():
    #  # Load config from file
    # with open("config.json") as f:
    #     configdata = json.load(f)
    
    #     deviceList = []
    #     for d in configdata["devices"]:
    #         device = Device( d.get("name"),
    #             d.get("ip"),
    #             d.get("type"),
    #             d.get("make"),
    #             d.get("id"),
    #             d.get("key"))
            
    #         if(device.type == "light"):
    #                 device:Device = get_device_by_ip(device.ip) 
    #                 try:   
    #                     if(device.ip != "0.0.0.0"):  # for testing purposes
    #                         print('Connecting to bulb %r ...' % device.ip)
    #                         b = tinytuya.BulbDevice(device.id,device.ip,device.key)
    #                         #b.connection_timeout(1000)
    #                         b.set_version(3.3) 
    #                         data = b.status()                            

    #                         #get current colour
    #                         currentcolour = decode_hsv_hex_to_rgb_hex(data["dps"]["24"])

    #                         #getcurrentbrightness
    #                         brightness = get_brightness_from_hex(data["dps"]["24"])

    #                         newBulb = Bulb(d.get("name"),
    #                         d.get("ip"),
    #                         d.get("type"),
    #                         d.get("make"),
    #                         d.get("id"),
    #                         d.get("key"),
    #                         data["dps"]["20"],
    #                         brightness,
    #                         currentcolour)

                            
    #                         print('colour')
    #                         print(currentcolour)

    #                         deviceList.append(newBulb) 
    #                         print('Connection Successful!') 
    #                     else: 
    #                         deviceList.append(device)
    #                 except:
    #                     deviceList.append(device)
    #                     print('Connection Failed.')
    #         else:                
    #             deviceList.append(device)

            

        

        

    return render_template("devices.html",deviceList=get_all_device_objs())

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
    #deviceList = get_all_devices()

    with open("config.json", 'r') as f:
        configdata = json.load(f)

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

    return render_template("dashboard.html", deviceList=get_all_device_objs(), weather=weather_data)


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
    deviceList = get_all_device_objs()
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

@views.route('/settings', methods=['GET', 'POST'])
def settings():
    CONFIG_PATH = os.path.join(os.getcwd(), 'config.json')
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    if request.method == 'POST':
        try:
            # Top-level values
            config['weather']['weather_api_key'] = request.form.get('weather_api_key', config['weather']['weather_api_key'])
            config['weather']['city'] = request.form.get('city', config['weather']['city'])

            # Nested: Spotify
            config['spotify']['client_id'] = request.form.get('spotify_client_id', config['spotify']['client_id'])
            config['spotify']['client_secret'] = request.form.get('spotify_client_secret', config['spotify']['client_secret'])

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

    return render_template('dashboardSettings.html', config=config)

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
            connect_to_firestick(ip)
    except:
        connect_to_firestick(ip)
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

### Functions ###

def connect_to_firestick(ip):
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        run_path = os.path.join(base_path, "adb")
        script_path = os.path.join(base_path, "adb", "adbconnect") 

        try:
            # result = subprocess.run(
            #     ["cmd.exe", "/c", bat_file, ip],
            #     cwd=run_path,
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )
                # Launches visible command prompt
            # result = subprocess.Popen(
            #     ["cmd.exe", "/k", bat_file, ip],  # /k keeps the window open
            #     cwd=run_path
            # )

            if platform.system() == "Windows":
                script_path += ".bat"
                result = subprocess.Popen(["cmd.exe", "/k", script_path, ip], cwd=run_path)
            else:
                script_path += ".sh"
                result = subprocess.run(["x-terminal-emulator", "-e", f"{script_path} {ip}"], cwd=run_path)
            print("Output:", result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
        return e.stderr
    

def get_all_device_objs():
     # Load config from file
    with open("config.json") as f:
        configdata = json.load(f)
    
        deviceList = []
        for d in configdata["devices"]:
            device = Device( d.get("name"),
                d.get("ip"),
                d.get("type"),
                d.get("make"),
                d.get("id"),
                d.get("key"))
            
            if(device.type == "light"):
                    device:Device = get_device_by_ip(device.ip) 
                    try:   
                        if(device.ip != "0.0.0.0"):  # for testing purposes
                            print('Connecting to bulb %r ...' % device.ip)
                            b = tinytuya.BulbDevice(device.id,device.ip,device.key)
                            #b.connection_timeout(1000)
                            b.set_version(3.3) 
                            data = b.status()                            

                            if(data['dps']['21'] == 'white'):
                                currentcolour = '#ffffff'
                            else:
                                #get current colour
                                currentcolour = decode_hsv_hex_to_rgb_hex(data["dps"]["24"])

                            #getcurrentbrightness
                            brightness = get_brightness_from_hex(data["dps"]["24"])

                            newBulb = Bulb(d.get("name"),
                            d.get("ip"),
                            d.get("type"),
                            d.get("make"),
                            d.get("id"),
                            d.get("key"),
                            data["dps"]["20"],
                            brightness,
                            currentcolour)

                            
                            print('colour')
                            print(currentcolour)

                            deviceList.append(newBulb) 
                            print('Connection Successful!') 
                        else: 
                            deviceList.append(device)
                    except:
                        deviceList.append(device)
                        print('Connection Failed.')
            else:                
                deviceList.append(device)
    return deviceList            

def get_device_by_ip(ip):
    with open("config.json") as f:
        config = json.load(f)
    
    for device in config.get("devices", []):
        if device.get("ip") == ip:
            return Device(
            device.get("name"),
            device.get("ip"),
            device.get("type"),
            device.get("make"),
            device.get("id"),
            device.get("key")
            )

    return None 

def get_all_devices():
    with open("config.json") as f:
        config = json.load(f)
    
    deviceList = []
    for device in config.get("devices", []):
        deviceList.append(Device(
            device.get("name"),
            device.get("ip"),
            device.get("type"),
            device.get("make"),
            device.get("id"),
            device.get("key")
            ))
    
    return deviceList  

def decode_hsv_hex_to_rgb_hex(hsv_hex):
    if len(hsv_hex) != 12:
        raise ValueError("HSV hex must be exactly 12 characters")

    # Step 1: Extract HSV values from hex
    h = int(hsv_hex[0:4], 16)
    s = int(hsv_hex[4:8], 16)
    v = int(hsv_hex[8:12], 16)

    # Step 2: Convert HSV to RGB
    s /= 1000.0
    v /= 1000.0

    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r1, g1, b1 = c, x, 0
    elif 60 <= h < 120:
        r1, g1, b1 = x, c, 0
    elif 120 <= h < 180:
        r1, g1, b1 = 0, c, x
    elif 180 <= h < 240:
        r1, g1, b1 = 0, x, c
    elif 240 <= h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = int((r1 + m) * 255)
    g = int((g1 + m) * 255)
    b = int((b1 + m) * 255)

    # Step 3: Convert RGB to hex
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def get_brightness_from_hex(code):
    if len(code) != 12:
        raise ValueError("Hex string must be 12 characters (6 bytes).")
    
    brightness_hex = code[-4:]  # last 4 hex chars = brightness
    brightness = int(brightness_hex, 16)  # convert to int
    brightness_percent = (brightness / 1000) * 100

    return round(brightness_percent)

### Control Devices Endpoints ###

@views.route('/lampswitch/<ip>', methods=['POST'])
def lampswitch(ip):
    device:Device = get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3) 
    
    data = d.status()
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

# /lampbright/<ip> - Toggles brightness between 25 , 100 , 255
@views.route('/lampbright/<ip>', methods=['GET','POST'])
def lampbright(ip):
    device:Device = get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3)  
    
    data = d.status()
    d.turn_on()
    if data['dps']['21'] == 'colour':
        brightness = get_brightness_from_hex(data["dps"]["24"])
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
    print(data)
    return "Success"

# /lampbright/{ip,brightness} - sets brightness to to a percentage value. 
@views.route('/setlampbright', methods=['GET','POST'])
def setlampbright():
    data = request.get_json()
    ip = data['ip']
    brightness = data['brightness']

    device:Device = get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3)  
    
    data = d.status()    
    d.turn_on()
    
    print(int(brightness))
    if(int(brightness) == 0):
        d.turn_off()
    else:
        d.set_brightness_percentage(int(brightness))

    data = d.status()
    print(data)
    
    return "Success"

# /lampbright/{ip,colour(hex)} - Sets colour of the light
@views.route('/setcolour', methods=['GET','POST'])
def setcolour():
    data = request.get_json()
    ip = data['ip']
    colour = data['colour']

    device:Device = get_device_by_ip(ip)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3)      
    data = d.status()
    d.turn_on()

    colour = colour[1:]
    c = hex_to_rgb(colour)
    if (colour == 'ffffff'):
        d.set_white(1000,10)
    else:
        c = hex_to_rgb(colour)
        d.set_colour(c[0],c[1],c[2])

    return "Success"

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

@views.route('/lightsoff', methods=['GET','POST'])
def lightsoff():
    #Light
    deviceList= get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            b.set_version(3.3)
            b.turn_off()

@views.route('/lightson', methods=['GET','POST'])
def lightson():
    #Light
    deviceList= get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            b.set_version(3.3)
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

@views.route('/moodlight', methods=['GET','POST'])
def moodlight():
    # taking the input from webcam
    vid = cv2.VideoCapture(0)

    d = tinytuya.BulbDevice(configdata['Light_ID_1'], configdata['Light_IP_1'], configdata['Light_KEY_1'])
    d.set_version(3.1)  # IMPORTANT to set this regardless of version
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

  
    # running while loop just to make sure that
    # our program keep running until we stop it
    while True:
        

        # capturing the current frame
        _, frame = vid.read()

        # displaying the current frame
        cv2.imshow("frame", frame)

        # setting values for base colors
        b = frame[:, :, :1]
        g = frame[:, :, 1:2]
        r = frame[:, :, 2:]

        # computing the mean
        b_mean = np.mean(b)
        g_mean = np.mean(g)
        r_mean = np.mean(r)

        #d.set_brightness(255)
          
        # # Set to RED Color - set_colour(r, g, b):
        d.set_colour(r_mean,g_mean,b_mean)
        #if(r>255):
         #   r = 255
        #if(g>255):
        #   g = 255
        #if(b>255):
         #   b=255
            
        #d.set_colour(r,g,b)
        data = d.status()
        #print('r'+str(r),'g'+str(g), 'b'+ str(b))
        print('R'+str(r_mean),'G'+str(g_mean),'B'+str(b_mean))
        #print('set_status() result %r' % data)

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

@views.route('spotify/spotify_status', methods=['GET','POST'])
def spotify_status():
    track = get_current_track()
    if track:
        return jsonify(track)
    return jsonify({"error": "No track playing or not authenticated."})

# Google

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRETS_FILE = "google.json"

@views.route('/authorize' , methods=['GET','POST'])
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('views.oauth2callback', _external=True))
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(auth_url)

@views.route('google/callback', methods=['GET','POST'])
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('views.oauth2callback', _external=True))
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
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

