import os
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen

class fireStickController():
    def __init__(self):
        if not os.path.isfile('adbkey'):
            print('Generating ADB Keys')
            keygen('adbkey')
        else:
            print('ADB Keys Found')

        with open('adbkey') as f:
            priv = f.read()
        with open('adbkey'+'.pub') as f:
            pub = f.read()
        self.creds = PythonRSASigner(pub,priv)

    def addDevice(self, deviceIP):
        self.device = AdbDeviceTcp(deviceIP, 5555, default_transport_timeout_s=9.)
        try:
            self.device.close()
        except:
            print ('No Device Connected')
        else:
            self.device.connect(rsa_keys=[self.creds], auth_timeout_s=10.)
            print ('Device Connected')

        return self.device

    def select(self):
        self.device._service(b'shell', b'input keyevent 23')
        print ('Select Command Sent')
    def back(self):
        self.device._service(b'shell', b'input keyevent 4')
        print ('Back Command Sent')
    def up(self):
        self.device._service(b'shell', b'input keyevent 19')
        print ('Up Command Sent')
    def down(self):
        self.device._service(b'shell', b'input keyevent 20')
        print ('Down Command Sent')    
    def right(self):
        self.device._service(b'shell', b'input keyevent 22')
        print ('Right Command Sent')
    def left(self):
        self.device._service(b'shell', b'input keyevent 21')
        print ('Left Command Sent')
    def playpause(self):
        self.device._service(b'shell', b'input keyevent 85')
        print ('Play/Pause Command Sent')
    def home(self):
        self.device._service(b'shell', b'input keyevent 3')
        print ('Home Command Sent')
    def menu(self):
        self.device._service(b'shell', b'input keyevent 1')
        print ('Menu Command Sent')
    def next(self):
        self.device._service(b'shell', b'input keyevent 87')
        print ('Next Command Sent')
    def prev(self):
        self.device._service(b'shell', b'input keyevent 88')
        print ('Previous Command Sent')   
    def poweroff(self):
        self.device._service(b'shell', b'input keyevent 223')
        print ('Power Down Command Sent')


    

    


# if __name__=='__main__':
#     fireStickIP = '192.168.15.13'

#     mc = fireStickController()
#     mc.addDevice(fireStickIP)
#     mc.down()
#     mc.down()
#     mc.right()
#     mc.right()
#     mc.right()
#     mc.select()

#     mc.up()
#     mc.right()
#     mc.select()

