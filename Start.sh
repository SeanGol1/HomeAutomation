#!/bin/bash

# Navigate to the script's directory
cd "$(/home/pi/HomeAutomation "$0")"
cd "/home/pi/HomeAutomation"

# Optional: activate virtual environment
# source venv/bin/activate

# Run the Python script
python3 main.py

# Optional: log output to a file
# python3 main.py >> log.txt 2>&1