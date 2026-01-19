from time import time
from flask import Blueprint, json
from ..services import fireStickController

firestick = Blueprint('firestick', __name__)

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

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
    