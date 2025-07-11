from distutils.command.config import config
from multiprocessing.connection import wait
from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify
#from . import fireStickController
import json , time , tinytuya , cv2, numpy as np

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

### WEBSITE ROUTES ###
@views.route('/')
def home():    
    return render_template("home.html")

@views.route('/devices', methods=['GET','POST'])
#@login_required
def light():
     # Load config from file
    with open("config.json") as f:
        configdata = json.load(f)

    deviceList = []
    for d in configdata["devices"]:
        deviceList.append(Device(
            d.get("name"),
            d.get("ip"),
            d.get("type"),
            d.get("make"),
            d.get("id"),
            d.get("key")
        ))

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


@views.route('/lampswitch/<ip>', methods=['GET','POST'])
def lampswitch(ip):
    device:Device = get_device_by_ip(ip)
    #print(device.id + ' ----- ' + device.ip + ' ----- ' + device.key)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3) 
    
    data = d.status()
    
    if data['dps']['20'] == False:
        d.turn_on()
        d.set_white(255,255)
        d.set_brightness(255)
    else:
        d.turn_off()

    return "Success"

# /lampbright/<ip> - Toggles brightness between 25 , 100 , 255
@views.route('/lampbright/<ip>', methods=['GET','POST'])
def lampbright(ip):
    device:Device = get_device_by_ip(ip)
    #print(device.id + ' ----- ' + device.ip + ' ----- ' + device.key)
    
    d = tinytuya.BulbDevice(device.id,device.ip,device.key)
    d.set_version(3.3)  
    
    data = d.status()
    data = d.status()
    d.turn_on()
    
    if data['dps']['22'] == 255:
        d.set_brightness(25)
        #update = 'Light set to dim brightness'
    elif data['dps']['22'] == 25:
        d.set_brightness(100)
        #update = 'Light set to medium brightness'
    else:
        d.set_brightness(255)

    return "Success"

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
    data = d.status()
    d.turn_on()
    print(int(brightness))
    if(int(brightness) == 0):
        d.turn_off()
    else:
        d.set_brightness_percentage(int(brightness))

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