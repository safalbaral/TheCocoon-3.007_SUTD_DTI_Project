import time
import microcontroller
import os
import ssl
import wifi
import socketpool
from adafruit_io.adafruit_io import IO_HTTP
import adafruit_requests

################ Wifi Connection ################
try:
    if wifi.radio.ipv4_address is None:
        print("connecting to wifi")
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'),
                        os.getenv('CIRCUITPY_WIFI_PASSWORD'))
        print(f"local address {wifi.radio.ipv4_address}")
except Exception as e:
    print("Failed to connect to Wi-Fi: ", repr(e))
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    microcontroller.reset()

aio_username = os.getenv('AIO_USERNAME')
aio_key = os.getenv('AIO_KEY')

################ Initialise HTTP ################
try:
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    # Initialize an Adafruit IO HTTP API object
    io = IO_HTTP(aio_username, aio_key, requests)
    print("connected to io") 
except Exception as e:
    print("Error in network setup:\n", repr(e))
    print("Resetting microcontroller in 20 seconds")
    time.sleep(20)
    microcontroller.reset()

# Get feeds
sensor_feed = io.get_feed("project.sensor-data")
scenario_feed = io.get_feed("project.scenario")