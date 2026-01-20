from time import time
from urllib import request
from flask import Blueprint, json, render_template

from website import functions
from ..services import fireStickController
from ppadb.client import Client as AdbClient #pip install pure-python-adb

firestick = Blueprint('firestick', __name__)

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)



@firestick.route("/remote/<ip>", methods=["GET", "POST"])
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

@firestick.route('/next_episode', methods=['GET','POST'])
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

@firestick.route('/recent_show', methods=['GET','POST'])
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

@firestick.route('/playpause', methods=['GET','POST'])
def playpause():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    
    mc.addDevice(fireStickIP)
    mc.playpause()
    
@firestick.route('/poweroff', methods=['GET','POST'])
def powerdown():
    fireStickIP = configdata['firestick_IP']
    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.poweroff()

@firestick.route('/formula1', methods=['GET','POST'])
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

@firestick.route('/wakeup', methods=['GET','POST'])
def wakeup():
    fireStickIP = configdata['firestick_IP']

    mc = fireStickController.fireStickController()
    mc.addDevice(fireStickIP)
    mc.home()
    