#!/bin/bash
export PATH=$PATH:/nix/store
export CHROME_BIN=$(which chromium)
export CHROMEDRIVER_PATH=$(which chromedriver)

echo "Chrome located at: $CHROME_BIN"
echo "Chromedriver located at: $CHROMEDRIVER_PATH"

python3 app.py