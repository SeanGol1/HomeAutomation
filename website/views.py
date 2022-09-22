from distutils.command.config import config
from multiprocessing.connection import wait
from turtle import update
from flask import Blueprint, render_template, request, flash, jsonify
from . import fireStickController
import json , time , tinytuya , cv2, numpy as np

views = Blueprint('views', __name__)
configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)


@views.route('/')
def home():    
    return render_template("home.html")


### Control Lights ###
@views.route('/lightswitch', methods=['GET','POST'])
def lightswitch():
    #Light
    d = tinytuya.BulbDevice(configdata['Light_ID_1'], configdata['Light_IP_1'], configdata['Light_KEY_1'])
    d.set_version(3.3)
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

    data = d.status()
    #print('set_status() result %r' % data)
    #time.sleep(2)
    print(data)
    if data['dps']['20'] == False:
        d.turn_on()
    else:
        d.turn_off()


@views.route('/lightbright', methods=['GET','POST'])
def lightbright():
    #Light
    d = tinytuya.BulbDevice(configdata['Light_ID_1'], configdata['Light_IP_1'], configdata['Light_KEY_1'])
    d.set_version(3.3)
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands
    data = d.status()
    d.turn_on()
    if data['dps']['22'] == 1000:
        d.set_brightness(100)
    elif data['dps']['22'] == 100:
        d.set_brightness(500)
    else:
        d.set_brightness(1000)

@views.route('/hallswitch', methods=['GET','POST'])
def hallswitch():
    #Light
    d = tinytuya.BulbDevice(configdata['Light_ID_2'], configdata['Light_IP_2'], configdata['Light_KEY_2'])
    d.set_version(3.3)
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

    data = d.status()
    #print('set_status() result %r' % data)
    #time.sleep(2)
    print(data)
    if data['dps']['20'] == False:
        d.turn_on()
    else:
        d.turn_off()

@views.route('/hallbright', methods=['GET','POST'])
def hallbright():
    #Light
    d = tinytuya.BulbDevice(configdata['Light_ID_2'], configdata['Light_IP_2'], configdata['Light_KEY_2'])
    d.set_version(3.3)
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

    data = d.status()
    d.turn_on()
    if data['dps']['22'] == 1000:
        d.set_brightness(100)
    elif data['dps']['22'] == 100:
        d.set_brightness(500)
    else:
        d.set_brightness(1000)

@views.route('/lampswitch', methods=['GET','POST'])
def lampswitch():
    d = tinytuya.BulbDevice(configdata['Light_ID_3'], configdata['Light_IP_3'], configdata['Light_KEY_3'])
    d.set_version(3.1)  # IMPORTANT to set this regardless of version
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands
    
    data = d.status()
    print('set_status() result %r' % data)
    

    if data['dps']['1'] == False:
        d.turn_on()
        #d.set_white(255,255)
        #d.set_brightness(255)
    else:
        d.turn_off()

@views.route('/lampbright', methods=['GET','POST'])
def lampbright():
    d = tinytuya.BulbDevice(configdata['Light_ID_3'], configdata['Light_IP_3'], configdata['Light_KEY_3'])
    d.set_version(3.1)  # IMPORTANT to set this regardless of version
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

    data = d.status()
    d.turn_on()
    

    #update = ''
    if data['dps']['3'] == 255:
        d.set_brightness(25)
        #update = 'Light set to dim brightness'
    elif data['dps']['3'] == 25:
        d.set_brightness(100)
        #update = 'Light set to medium brightness'
    else:
        d.set_brightness(255)

@views.route('/light', methods=['GET','POST'])
#@login_required
def light():
    return render_template("light.html")

@views.route('/lightsoff', methods=['GET','POST'])
def lightsoff():
    #Light
    d = tinytuya.BulbDevice(configdata['Light_ID_1'], configdata['Light_IP_1'], configdata['Light_KEY_1'])
    e = tinytuya.BulbDevice(configdata['Light_ID_2'], configdata['Light_IP_2'], configdata['Light_KEY_2'])
    f = tinytuya.BulbDevice(configdata['Light_ID_3'], configdata['Light_IP_3'], configdata['Light_KEY_3'])
    d.set_version(3.3)
    d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands
    e.set_version(3.1)
    e.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands
    f.set_version(3.3)
    f.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

    d.turn_off()
    e.turn_off()
    f.turn_off()
        

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