#!/bin/bash

# Navigate to your app directory
cd "/home/pi/HomeAutomation" || exit

# Ensure Avahi (mDNS) service is running
echo "Starting Avahi daemon..."
sudo systemctl start avahi-daemon
sudo systemctl enable avahi-daemon

# Optional: activate virtual environment
# source venv/bin/activate

# Run the Python script
echo "Starting app..."
python3 main.py

# Optional: log output to a file