import time
import board
import busio
import pwmio
import microcontroller
import json
import os
import ssl
import wifi
import socketpool
from adafruit_io.adafruit_io import IO_MQTT
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_dht
import adafruit_bh1750
import adafruit_vl53l0x
from adafruit_motor import motor
from pioasm_neopixel_bg import NeoPixelBackground
import rainbowio
import supervisor

import neopixel

from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.color import (
    PURPLE,
    WHITE,
    AMBER,
    JADE,
    TEAL,
    AQUA,
    MAGENTA,
    ORANGE,
    YELLOW,
    GREEN,
)

################ Constants for program settings ################
test_motor = False  # Power Motor up?
internet = False    # Connect to internet?


################ Initialise hardware ################
i2c = busio.I2C(scl=board.GP13, sda=board.GP12, frequency=50000)

try:
    while not i2c.try_lock():
        pass
    print(
        "I2C addresses found:",
        [hex(device_address) for device_address in i2c.scan()],
    )
    i2c.unlock()

    tof_sensor = adafruit_vl53l0x.VL53L0X(i2c)
    light_sensor = adafruit_bh1750.BH1750(i2c)

    dht_sensor = adafruit_dht.DHT11(board.GP14)
except Exception as e:
    print('Critical Error initializing sensors:', repr(e))
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    error_count = 0
    microcontroller.reset()

pwm16_motor1 = pwmio.PWMOut(board.GP16, frequency=1000)
pwm17_motor1 = pwmio.PWMOut(board.GP17, frequency=1000)
motor_1 = motor.DCMotor(pwm16_motor1, pwm17_motor1)
motor_1.decay_mode = (motor.SLOW_DECAY)

pwm15_ledfilament = pwmio.PWMOut(board.GP15, frequency=1000)
pwm11_ledfilament = pwmio.PWMOut(board.GP11, frequency=1000)
pwm10_ledfilament = pwmio.PWMOut(board.GP10, frequency=1000)

# Neopixel init
pavilion_pixels = neopixel.NeoPixel(board.GP22, 7, brightness=0.5, auto_write=False)

comet = Comet(pavilion_pixels, speed=0.01, color=PURPLE, tail_length=10, bounce=True)
pulse_white = Pulse(pavilion_pixels, speed=0.05, color=YELLOW, period=5)
pulse_green = Pulse(pavilion_pixels, speed=0.05, color=ORANGE, period=5)
sparkle_lightblue = SparklePulse(pavilion_pixels, speed=0.05, color=AQUA, period=5, max_intensity=0.3, min_intensity=0.1)
# sparkle_lightblue = Sparkle(pavilion_pixels, speed=0.2, color=AQUA, num_sparkles=5)
pavilion_rain_anim = AnimationSequence(
    pulse_white,
    pulse_green,
    advance_interval=5,
    auto_clear=False,
)

pavilion_night_anim = AnimationSequence(
    sparkle_lightblue,
    advance_interval=5,
    auto_clear=False,
)

################ MQTT Callbacks ################
# pylint: disable=unused-argument
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    print("Connected to Adafruit IO! ")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")

def on_scenario_msg(client, topic, message):
    # Method called whenever project.scenario has a new value
    #print("New message on topic {0}: {1} ".format(topic, message))
    # one scenario will last forever until it has been turned off
    if topic == 'neelonoon/f/project.scenario':
        if message == 's1':
            print('scenario 1 invoked')
        elif message == 's2':
            print('scenario 2 invoked')
        elif message == 's3':
            print('scenario 3 invoked')
        elif message == 's4':
            print('scenario 4 invoked')

################ Helper Functions ################

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5

################ Wifi Connection ################
try:
    if wifi.radio.ipv4_address is None and internet:
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

################ Initialise MQTT ################
try:
    if internet:
        pool = socketpool.SocketPool(wifi.radio)
        mqtt_client = MQTT.MQTT(
            broker="io.adafruit.com",
            port=1883,
            username=aio_username,
            password=aio_key,
            socket_pool=pool,
            ssl_context=ssl.create_default_context()
        )
        # Initialize an Adafruit IO MQTT Client
        io = IO_MQTT(mqtt_client)
        # Setup callbacks here
        io.on_connect = connected
        io.on_disconnect = disconnected
        io.on_subscribe = subscribe
        io.add_feed_callback("project.scenario", on_scenario_msg)
        io.connect()
        print("connected to io")
        # Setup subscribes here
        io.subscribe("project.scenario")
except Exception as e:
    print("Error in network setup:\n", repr(e))
    print("Resetting microcontroller in 20 seconds")
    time.sleep(20)
    microcontroller.reset()

################ List of sensors ################
SENSOR_LIST = [
    {
        "ON": 2,                # Trigger time, every 2 seconds
        "PREV_TIME": -1,
        "OBJECT": light_sensor,
        "LUX_VALUE": -1
    },
    {
        "ON": 2,
        "PREV_TIME": -1,
        "OBJECT": dht_sensor,
        "TEMP_VALUE": -1,       # Temperature in deg C
        "HUMD_VALUE": -1,       # Humidity in percentage
        "HEATIND_VALUE": -1     # Heat index
    },
    {
        "ON": 1,
        "PREV_TIME": -1,
        "OBJECT": tof_sensor,
        "VALUES": [],
        "PRESENCE_VALUE": "No"
    }
]

if internet:
    SENSOR_LIST.append({
        "ON": 4,
        "PREV_TIME": -1,
        "OBJECT": io
    })

MOTOR_LIST = [
    {
        "ON": 5,            # Interval to switch on for
        "OFF": 5,           # Interval to switch off for
        "PREV_TIME": -1,    # Previous time
        "MOTOR": motor_1    # Motor object
    }
]

LIGHT_LIST = [
    {
        "ON": 0.01,
        "OFF": 5,
        "PREV_TIME": -1,
        "PIN": pwm11_ledfilament,
        "PWM": 0, # note: this is a 16-bit integer, maximum 0xffff
        "FADE_DIR": True
    },
    {
        "ON": 0.01,
        "OFF": 5,
        "PREV_TIME": -1,
        "PIN": pwm10_ledfilament,
        "PWM": 0, # note: this is a 16-bit integer, maximum 0xffff
        "FADE_DIR": True
    },
    {
        "ON": 0.01,
        "OFF": 5,
        "PREV_TIME": -1,
        "PIN": pwm15_ledfilament,
        "PWM": 0, # note: this is a 16-bit integer, maximum 0xffff
        "FADE_DIR": True
    }
]

print('sleeping before activation...')
time.sleep(5)
print('activated!')

error_count = 0

while True:
    try:
        pavilion_night_anim.animate()
        now = time.monotonic()
        # ping adafruit MQTT. known bug that this will be blocking and cause delays, so account for it accordingly
        # try:
        #     if internet:
        #         io.loop()
        # except Exception as e:
        #     print('io.loop exception:', repr(e))

        # This section reads live data from sensors and sends them
        for sensor in SENSOR_LIST:
            if now >= sensor["PREV_TIME"] + sensor["ON"]:
                if type(sensor["OBJECT"]) is adafruit_bh1750.BH1750:
                    sensor["PREV_TIME"] = now
                    print("%.2f Lux" % sensor["OBJECT"].lux)
                    sensor["LUX_VALUE"] = sensor["OBJECT"].lux

                if type(sensor["OBJECT"]) is adafruit_dht.DHT11:
                    sensor["PREV_TIME"] = now
                    try:
                        temperature_c = sensor["OBJECT"].temperature
                        humidity = sensor["OBJECT"].humidity
                        if type(temperature_c) is None:
                            print('is none!!!')
                        else:
                            temperature_f = temperature_c * (9 / 5) + 32
                            sensor["TEMP_VALUE"] = temperature_c
                            sensor["HUMD_VALUE"] = humidity
                            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))
                    except RuntimeError as error:
                        # Errors happen fairly often, DHT's are hard to read, just keep going
                        print('DHT error: ', error.args[0])
                        pass
                    except Exception as error:
                        print('DHT related error: ', error.args[0])
                        pass
                
                if type(sensor["OBJECT"]) is adafruit_vl53l0x.VL53L0X:
                    sensor["PREV_TIME"] = now
                    sensor["VALUES"].append(sensor["OBJECT"].range)
                    if len(sensor["VALUES"]) > 10:
                        sensor["VALUES"].pop(0)
                    if len(sensor["VALUES"]) > 4:
                        # Human presence is based on whether the standard deviation exceeds 5, which is reasonable
                        sensor["PRESENCE_VALUE"] = 'Present' if stddev(sensor["VALUES"]) > 5 else 'Not Present'
                        print('ToF Standard Deviation: {}mm'.format(stddev(sensor["VALUES"])))
                
                if type(sensor["OBJECT"]) is IO_MQTT:
                    sensor["PREV_TIME"] = now
                    # Package up all the data and send it to MQTT
                    try:
                        io.publish('project.sensor-data', json.dumps({
                            "Temperature": SENSOR_LIST[1]["TEMP_VALUE"],
                            "Humidity": SENSOR_LIST[1]["HUMD_VALUE"],
                            "Human Activity": SENSOR_LIST[2]["PRESENCE_VALUE"],
                            "Luminosity": round(SENSOR_LIST[0]["LUX_VALUE"],2)
                        }))
                    except Exception as e:
                        print('Error sending data to IO:', repr(e))
                        print(f"Local address {wifi.radio.ipv4_address}")
                        raise e

        # every 2 seconds, motor on, motor off, motor reverse, motor off
        if test_motor:
            for motor in MOTOR_LIST:
                if motor["MOTOR"].throttle == -1:
                    if now >= motor["PREV_TIME"] + motor["ON"]:
                        # Action to do when motor is transitioning from ON to OFF
                        motor["PREV_TIME"] = now
                        motor["MOTOR"].throttle = 1
                if motor["MOTOR"].throttle == 1 or motor["MOTOR"].throttle == None:
                    if now >= motor["PREV_TIME"] + motor["OFF"]:
                        # Action to do when motor is transitioning from OFF to ON
                        motor["PREV_TIME"] = now
                        motor["MOTOR"].throttle = -1

        # for light in LIGHT_LIST:
        #     if now >= light["PREV_TIME"] + light["ON"]:
        #         if light["FADE_DIR"] == True:
        #             # increase brightness
        #             light["PWM"] += 255
        #         elif light["FADE_DIR"] == False:
        #             # decrease brightness
        #             light["PWM"] -= 255
                
        #         # apply changes
        #         light["PIN"].duty_cycle = light["PWM"]
        #         light["PREV_TIME"] = now

        #         # change direction of fade
        #         if light["PWM"] < 0x0002:
        #             light["FADE_DIR"] = True
        #             # increase brightness
        #         elif light["PWM"] > 0xfff1:
        #             light["FADE_DIR"] = False
        #             # decrease brightness
    except Exception as e:
        print('General Error Detected:', repr(e))
        error_count += 1
        print('Error Count:', error_count)
        if error_count > 5:
            print("Resetting microcontroller in 10 seconds")
            time.sleep(20)
            error_count = 0
            microcontroller.reset()
