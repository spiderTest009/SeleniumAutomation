#!/bin/bash

# Start Xvfb (virtual display)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Start the Flask app
python app.py