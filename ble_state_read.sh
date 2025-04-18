#!/bin/bash

# Read the BLE state from the device
poetry run smpmgr --timeout 120 --ble EE:67:F5:83:61:65 image state-read

