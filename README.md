# Smart Home Dashboard & API

## Overview  
This app is a smart home automation dashboard and API system designed to run on a local server — ideally a Raspberry Pi. It allows you to control various devices in your home using web-based commands or by scanning NFC tags that trigger API requests.

## How it Works  
- Install and run the Flask app on your home server (Raspberry Pi recommended).  
- The server exposes a web dashboard and a set of API endpoints to control smart devices like lights and Firestick TVs.  
- You can place NFC tags around your house that are programmed to hit specific endpoints when scanned (e.g. turn off all lights, play a show, etc.).  
- The dashboard allows you to monitor and control all configured devices in one place.

## Hardware Requirements  
- Raspberry Pi (or any always-on server)  
- Smart Bulbs that work with Tuya (TinyTuya compatible)  
- Firestick TV (for Firestick integration)  
- NFC Tags (optional but powerful for automation)

## Technologies Used  
- Python 3  
- Flask web framework  
- TinyTuya library for smart bulb control  
- OpenCV and NumPy for webcam-based mood lighting  
- JavaScript (Fetch API) for frontend interactions  
- HTML/CSS/Bootstrap for dashboard UI

## Available API Endpoints  

| Endpoint           | Method    | Arguments                               | Description                                         |
|--------------------|-----------|-----------------------------------------|-----------------------------------------------------|
| /devices           | GET       |                                         | Displays all configured devices in the dashboard.   |
| /addDevice         | GET/POST  |                                         | Form and submission route for adding a new device.  |
| /lampswitch/<ip>   | GET       | IP Address {string}                     | Toggles power on/off for a smart bulb by IP address.|
| /lampbright/<ip>   | POST      | IP Address {string}                     | Toggles brightness levels (25%, 66%, 100%) for a bulb.|
| /setlampbright     | POST      | IP Address {string}, Brightness 0-100 {int} | Sets brightness for a bulb to a specific percentage.|
| /setcolour         | POST      | IP Address {string}, Colour Hex #000000 {string} | Changes the colour of the light using a hex code.   |
| /lightsoff         | GET/POST  |                                         | Turns off all configured smart lights.              |
| /next_episode      | GET/POST  |                                         | Navigates Firestick to play the next episode.       |
| /recent_show       | GET/POST  |                                         | Plays the most recently watched show on Firestick.  |
| /playpause         | GET/POST  |                                         | Toggles play/pause on the Firestick.                |
| /poweroff          | GET/POST  |                                         | Powers off the Firestick device.                    |
| /formula1          | GET/POST  |                                         | Launches the Formula 1 app on Firestick and starts playback. |
| /wakeup            | GET/POST  |                                         | Wakes up the Firestick and brings it to the home screen. |
| /moodlight         | GET/POST  |                                         | Reads the average colour from your webcam and adjusts light colour to match. |

## NFC Automation Ideas  
- Stick an NFC tag by your front door that turns off all lights when you leave.  
- Place a tag near your bed that dims the lights and starts your favorite show.  
- Use tags for specific moods: work mode, movie time, party lights, etc.

## How to Run the App on Raspberry Pi  

``` 1. Clone the repository and navigate to the project directory:

`git clone <repository-url>`  
`cd smart-home-dashboard`

``` 2. Install dependencies:  
Ensure Python 3 and pip are installed on your Raspberry Pi. Then install required Python packages:  

`pip install -r requirements.txt`

``` 3. Configure devices:  
Edit the `config.json` file and add your smart devices’ IPs, IDs, and keys.

``` 4. Run the Flask app:  
Start the Flask server with:  

`python app.py`

This will start the server on port 5000 and make it available over the local network.

``` 5. Access the dashboard:  
From any device on your network, visit:  

`http://<raspberry-pi-ip>:5000`

``` 6. Optional - Keep app running in the background:  
Use `tmux`, `screen`, or a systemd service to ensure the app runs continuously even after closing the terminal.
