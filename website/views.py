#from distutils.command.config import config
#from multiprocessing.connection import wait
# from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify ,  make_response, redirect,url_for, session
import json , time , tinytuya ,  numpy as np , requests , speedtest, psutil , spotipy, subprocess, os, platform 
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import website.functions as functions 

views = Blueprint('views', __name__)


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

# staticTiles = ['weather-card','spotify-card', 'calendar-card' , 'general-controls-card' , 'website-controls-card', 
#                   'clock-card', 'voice-card', 'maps-card' , 'system-card', 'scenes-card', ]

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
        with open('configs/tiles.json') as t:
            tile_config = json.load(t)
        selected_tiles = tile_config.get('selected_tiles', [])
    except FileNotFoundError:
        selected_tiles = []

    try:
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
    except Exception as e:
        print("Spotify Error:", e)
        current_track = None


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

    # layout = []
    # with open('/configs/layout.json', 'w') as f:
    #     layout = json.load(f)

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

@views.route('/save-layout', methods=['POST'])
def save_layout(layout):
    layout = request.get_json()
    print("layout:", layout)

    with open('/configs/layout.json', 'w') as f:
        json.dump({"layout": layout}, f, indent=2)

    return redirect(url_for('views.dashboard'))

@views.route('/load-layout', methods=['GET'])
def load_layout():
    layout = []
    with open('configs/layout.json', 'r') as f:
        layout = json.load(f)

    return jsonify(layout)

### Voice Control Endpoint ###

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

@views.route('/lampswitch/<ip>', methods=['GET','POST'])
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
    d.close()
    return response


def lampswitch_int(ip,on):
    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,'Auto',device.key)
    d.set_version(device.version) 
    d.set_socketPersistent(False)

    isOn = False
    if on == True:
        d.turn_on()
        isOn = True
    else:
        d.turn_off()
        isOn = False
    print(jsonify(isOn))

    d.close()

    response = make_response("Success", 200)
    response.headers['Content-Type'] = 'application/json'
    return response

# TODO: unused 
# /lampbright/<ip> - Toggles brightness between 25 , 100 , 255
@views.route('/lampbright/<ip>', methods=['GET','POST'])
def lampbright(ip):
    device:Device = functions.get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,'Auto',device.key)
    d.set_version(device.version)  
    d.set_socketPersistent(False)
    
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
    d.close()
    #print(data)
    return "Success"

# /lampbright/{ip,brightness} - sets brightness to to a percentage value. 
@views.route('/setlampbright', methods=['GET','POST'])
def setlampbright():
    try:
        data = request.get_json()
        ip = data['ip']
        brightness = data['brightness']  

        d,data = functions.tinytuya_connect(ip)
        d.turn_on()
    
        #print(int(brightness))
        if(int(brightness) == 0):
            d.turn_off()
        else:
            d.set_brightness_percentage(int(brightness))

        data = d.status()
        #print(data)
        d.close()

        return "Success"

    except Exception as e:
        print("Error in setlampbright:", e)
    
    return "Error: "+ e, 500


def setlampbright_int(ip,brightness):
    # data = request.get_json()
    # ip = data['ip']
    # brightness = data['brightness']

    # device:Device = functions.get_device_by_ip(ip)    
    # d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    # d.set_version(device.version)  
    # d.set_socketPersistent(False)
    
    # data = d.status()    

    d,data = functions.tinytuya_connect(ip)
    d.turn_on()
    
    print('internal ' + int(brightness))
    if(int(brightness) == 0):
        d.turn_off()
    else:
        d.set_brightness_percentage(int(brightness))

    data = d.status()
    print(data)
    d.close()
    
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
    d.set_socketPersistent(False)    
    data = d.status()
    d.turn_on()

    colour = colour[1:]
    c = functions.hex_to_rgb(colour)
    if (colour.lower() == 'ffffff'):
        d.set_white(1000,10)
    else:
        c = functions.hex_to_rgb(colour)
        d.set_colour(c[0],c[1],c[2])

    d.close()

    return "Success"

# /lampbright/{ip,colour(hex)} - Sets colour of the light
def setcolour_int(ip,colour):
    device:Device = functions.get_device_by_ip(ip)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(device.version)
    d.set_socketPersistent(False)     
    data = d.status()
    d.turn_on()

    colour = colour[1:]
    c = functions.hex_to_rgb(colour)
    if (colour.lower() == 'ffffff'):
        d.set_white(1000,10)
    else:
        c = functions.hex_to_rgb(colour)
        d.set_colour(c[0],c[1],c[2])

    d.close()
    return "Success"

@views.route('/lightsoff', methods=['GET','POST'])
def lightsoff():
    #Light
    deviceList= functions.get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            d.set_socketPersistent(False)
            b.set_version(d.version)
            b.turn_off()

@views.route('/lightson', methods=['GET','POST'])
def lightson():
    #Light
    deviceList= functions.get_all_devices()
    for d in deviceList:
        if (d.type == "light"):
            b = tinytuya.BulbDevice(d.id, d.ip, d.key)
            d.set_socketPersistent(False)
            b.set_version(d.version)
            b.turn_on()
            b.close()



    
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


