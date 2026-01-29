import website.views as views
from flask import jsonify 
import json, os, platform,tinytuya,subprocess

# Development mode check
IS_DEVELOPMENT = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1'

# Voice Commands
def getAction(text):
    print ('made it to get action.')
    
    #actions = [{'text':'turn off','turn on','%','brightness','colour','color']
    actions = [{'text':'turn off','type':'light'},
                {'text':'turn on','type':'light'},
                {'text':'%','type':'light'},
                {'text':'brightness','type':'light'},
                {'text':'colour','type':'light'},
                {'text':'color','type':'light'}]

    devices = views.get_all_devices()
    for a in actions:
            if a['text'] in text:
                for d in devices:
                    if d.name.lower() in text: 
                        do_action(text,a,d)

                #If action found but not device. 
                if 'all' in text:
                    for d in devices:
                        if(d.type == a['type']):
                            do_action(text,a,d)        





        
    return "failure"

def do_action(text,a,d):
    # Light Controls
    if a['text'] == 'turn off' or a['text'] == 'turn on':
        views.lampswitch(d.ip)
        return "success"
    elif a['text']  == '%' or a['text']  == 'brightness':
        digits = ''.join(filter(str.isdigit, text))
        bdata = jsonify({'ip':d.ip, 'brightness':digits})
        if int(digits) < 101:
            views.setlampbright_int(d.ip,digits)
            return "success"
    elif a['text']  == 'colour' or a['text']  == 'color':
        colour = extract_color_from_text(text)
        if colour:
            views.setcolour_int(d.ip,colour)
            return "success"


def extract_color_from_text(text):
    # Define basic color mapping
    color_map = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "purple": "#800080",
        "pink": "#FFC0CB",
        "orange": "#FFA500",
        "white": "#FFFFFF",
        "black": "#000000",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        "warm white": "#FDF5E6",
        "cool white": "#F0F8FF",
    }

    # Normalize text
    lower_text = text.lower()

    # Search for color names
    for name, hex_value in color_map.items():
        if name in lower_text:
            return hex_value

    return None  # No recognized color found   

def get_all_devices():
    with open("config.json") as f:
        config = json.load(f)
    
    deviceList = []
    for device in config.get("devices", []):
        deviceList.append(views.Device(
            device.get("name"),
            device.get("ip"),
            device.get("type"),
            device.get("make"),
            device.get("id"),
            device.get("key"),
            device.get("version"),
            device.get("room")
            ))
    
    return deviceList  


def get_all_device_objs():
     # Load config from file
    with open("config.json") as f:
        configdata = json.load(f)
    
        deviceList = []
        for d in configdata["devices"]:
            device = views.Device( d.get("name"),
                d.get("ip"),
                d.get("type"),
                d.get("make"),
                d.get("id"),
                d.get("key"),
                d.get("version"),
                d.get("room"))
            
            if(device.type == "light" and not IS_DEVELOPMENT): 
                    #device:views.Device = get_device_by_ip(device.ip) 
                    try:   
                        if(device.ip != "0.0.0.0"):  # for testing purposes
                            print('Connecting to bulb '+ device.name+ ' (' + device.ip + ') ...')
                            b = tinytuya.BulbDevice(device.id,'Auto',device.key)
                            #b.connection_timeout(1000)
                            
                            b.set_version(device.version)
                            b.set_socketPersistent(False)
                            data = b.status()       
                            # print(b.address)
                            new_ip = b.address
                            b.close()
                            updated = False
                            for dev in configdata["devices"]:
                                if dev.get("id") == device.id and dev.get("ip") != new_ip:
                                    print(f"Updating IP from {dev['ip']} to {new_ip}")
                                    dev["ip"] = new_ip
                                    updated = True
                                    break
                            
                            if updated:
                                with open("config.json", "w") as f:
                                    json.dump(configdata, f, indent=4)
                                                 

                            if(data['dps']['21'] == 'white'):
                                currentcolour = '#ffffff'
                            else:
                                #get current colour
                                currentcolour = decode_hsv_hex_to_rgb_hex(data["dps"]["24"])

                            #getcurrentbrightness
                            brightness = get_brightness_from_hex(data["dps"]["24"])

                            newBulb = views.Bulb(d.get("name"),
                            d.get("ip"),
                            d.get("type"),
                            d.get("make"),
                            d.get("id"),
                            d.get("key"),               
                            d.get("version"),
                            d.get("room"),
                            data["dps"]["20"],
                            brightness,
                            currentcolour)

                            deviceList.append(newBulb) 
                            print('Connection Successful!') 

                        else: 
                            deviceList.append(device)
                    except(Exception) as e:
                        deviceList.append(device)
                        print('Connection Failed.' + str(e))

            else:                
                deviceList.append(device)
    return deviceList            

def get_device_by_ip(ip):
    with open("config.json") as f:
        config = json.load(f)
    
    for device in config.get("devices", []):
        if device.get("ip") == ip:
            return views.Device(
            device.get("name"),
            device.get("ip"),
            device.get("type"),
            device.get("make"),
            device.get("id"),
            device.get("key"),
            device.get("version"),
            device.get("room")
            )

    return None 



def get_all_scenes():
    with open('configs/scenes.json') as f:
        sceneconfig = json.load(f)
    return [{"name": name, "steps": steps} for name, steps in sceneconfig.items()]
    
def get_all_scenes_names():
    with open('configs/scenes.json') as f:
        sceneconfig = json.load(f)
    
    ip_to_name = {device.ip: device.name for device in get_all_devices()}

    scenes = []
    for name, steps in sceneconfig.items():
        updated_steps = []
        for step in steps:
            updated_steps.append({
                "device": ip_to_name.get(step["device"], step["device"]),
                "action": step["action"],
                "option": step["option"]
            })
        scenes.append({"name": name, "steps": updated_steps})

    return scenes

def get_all_scenes_with_device_names():
    scenes = get_all_scenes()
    device_list = get_all_device_objs()
    ip_to_name = {device.ip: device.name for device in device_list}
    
    enriched_scenes = []

    for scene in scenes:
        name = scene.get("name")
        steps = scene.get("steps", [])
        enriched_steps = []

        for step in steps:
            device_ip = step.get("device")
            device_name = ip_to_name.get(device_ip, device_ip)  # fallback to IP if no name
            enriched_step = {
                "device": device_name,
                "action": step.get("action"),
                "option": step.get("option")
            }
            enriched_steps.append(enriched_step)

        enriched_scenes.append({
            "name": name,
            "steps": enriched_steps
        })

    return enriched_scenes

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

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def tinytuya_connect(ip):
    device:views.Device = get_device_by_ip(ip)    
    d = tinytuya.BulbDevice(device.id,'Auto',device.key)
    d.set_version(device.version) 
    d.set_socketPersistent(False)
    
    data = d.status()
    return d,data


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


# def send_device_command(ip, action, option):
#     url = f"http://{ip}/action"
#     payload = {"action": action, "option": option}
#     try:
#         response = requests.post(url, json=payload, timeout=3)
#         return response.ok
#     except Exception as e:
#         print(f"Error sending to {ip}: {e}")
#         return False