import os
from flask import Blueprint, json, render_template, request, jsonify ,redirect, url_for
import website.functions as functions
from website.views import lampswitch_int, setcolour_int, setlampbright_int 

scenes = Blueprint('scenes', __name__)


### Scenes

# @scenes.route('/')
# def scenes():    
#     return render_template("dashboardScenes.html")


@scenes.route('/', methods=['GET', 'POST'])
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
            scenes_path = 'configs/scenes.json'
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

@scenes.route('/addScene', methods=['POST'])
def add_scene():
    try:
        # Get the posted data
        data = request.get_json()
        steps = data.get('steps', [])
        name = data.get('name','')

        # If scenes.config doesn't exist yet, start with empty dict
        if not os.path.exists('configs/scenes.json'):
            scenes_data = {}
        else:
            with open('configs/scenes.json', 'r') as f:
                try:
                    scenes_data = json.load(f)
                except json.JSONDecodeError:
                    scenes_data = {}

        # Generate a new scene name (you can enhance this later to accept custom names)
        scene_name = f"{name}"
        scenes_data[scene_name] = steps

        # Write updated data back to file
        with open('configs/scenes.json', 'w') as f:
            json.dump(scenes_data, f, indent=2)

        return jsonify({ "status": "success", "scene": scene_name }), 200

    except Exception as e:
        print(f"Error saving scene: {e}")
        return jsonify({ "status": "error", "message": str(e) }), 500

@scenes.route('/deleteScene/<scene_name>', methods=['POST'])
def delete_scene(scene_name):
    if not os.path.exists('configs/scenes.json'):
        return False, "Scene file not found."

    with open('configs/scenes.json', 'r') as f:
        scenes = json.load(f)

    if scene_name not in scenes:
        return False, "Scene not found."

    del scenes[scene_name]

    with open('configs/scenes.json', 'w') as f:
        json.dump(scenes, f, indent=2)

    return jsonify({ "status": "success", "scene": scene_name }), 200


def send_device_command(ip, action, option):

    if(action == 'state'):
        lampswitch_int(ip,option)
    elif(action == 'brightness'):
        setlampbright_int(ip,option)
    elif(action == 'colour'):
        setcolour_int(ip,option)
    

@scenes.route('/run_scene/<scene_name>', methods=['POST'])
def run_scene(scene_name):
    try:
        with open('configs/scenes.json') as f:
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
