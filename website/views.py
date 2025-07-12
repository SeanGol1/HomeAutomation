from distutils.command.config import config
from multiprocessing.connection import wait
from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify ,  make_response
#from . import fireStickController
import json , time , tinytuya , cv2, numpy as np , colorsys, re

views = Blueprint('views', __name__)
configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

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
#@login_required
def devices():
     # Load config from file
    with open("config.json") as f:
        configdata = json.load(f)
    try:
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
                    print(device)
                    b = tinytuya.BulbDevice(device.id,device.ip,device.key)
                    b.set_version(3.3) 
                    data = b.status()
                    print(data)

                    # hsv = extract_hsv_ranges(data["dps"]["24"])
                    # currentcolor = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[0])
                    currentcolour = decode_hsv_hex_to_rgb_hex(data["dps"]["24"])

                    # hsv = decode_hsv_hex(data["dps"]["24"])
                    # rgb = colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2])
                    # currentcolor = rgb_to_hex(rgb)

                    newBulb = Bulb(d.get("name"),
                    d.get("ip"),
                    d.get("type"),
                    d.get("make"),
                    d.get("id"),
                    d.get("key"),
                    data["dps"]["20"],
                    data["dps"]["22"],
                    currentcolour)

                    
                    print('colour')
                    print(currentcolour)

                    deviceList.append(newBulb)
            else:
                deviceList.append(device)
    except:
        deviceList.append(device)
            

        

        

    return render_template("devices.html",deviceList=deviceList)

@views.route('/addDevice', methods=['GET'])
#@login_required
def addDevice():
    return render_template("addDevice.html")

@views.route('/addDevice', methods=['POST'])
#@login_required
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
    # try:
    #     with open(CONFIG_FILE, 'r') as f:
    #         config = json.load(f)
    # except FileNotFoundError:
    #     config = {"devices": []}

    # Add the new device
    configdata["devices"].append(new_device)

    # Save back to file
    with open("config.json", 'w') as f:
        json.dump(configdata, f, indent=4)

    return render_template("devices.html")


### Control Lights ###

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


@views.route('/lampswitch/<ip>', methods=['GET'])
def lampswitch(ip):
    device:Device = get_device_by_ip(ip)
    #print(device.id + ' ----- ' + device.ip + ' ----- ' + device.key)
    
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
    #return jsonify(device.ip)

# /lampbright/<ip> - Toggles brightness between 25 , 100 , 255
@views.route('/lampbright/<ip>', methods=['GET','POST'])
def lampbright(ip):
    device:Device = get_device_by_ip(ip)
    #print(device.id + ' ----- ' + device.ip + ' ----- ' + device.key)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.4)  
    
    data = d.status()
    d.turn_on()
    
    if data['dps']['23'] == 255:
        d.set_brightness(25)
        print(25)
        #update = 'Light set to dim brightness'
    elif data['dps']['23'] == 25:
        d.set_brightness(100)
        print(100)
        #update = 'Light set to medium brightness'
    else:
        d.set_brightness(255)
        print(255)

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
    #print(device.id + ' ----- ' + device.ip + ' ----- ' + device.key)
    
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
    d.set_colour(c[0],c[1],c[2])

    return "Success"

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

@views.route('/lightsoff', methods=['GET','POST'])
def lightsoff():
    #Light
    deviceList= get_all_devices()
    for d in deviceList:
        b = tinytuya.BulbDevice(d.id, d.ip, d.key)
        b.set_version(3.3)
        b.turn_off()

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