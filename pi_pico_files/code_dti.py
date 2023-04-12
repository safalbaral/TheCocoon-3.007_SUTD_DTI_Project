import time
import board
import busio
import pwmio
import microcontroller
import adafruit_scd30
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

################ Initialise hardware ################
i2c = busio.I2C(scl=board.GP13, sda=board.GP12, frequency=50000)
light_sensor = adafruit_bh1750.BH1750(i2c)
tof_sensor = adafruit_vl53l0x.VL53L0X(i2c)

dht_sensor = adafruit_dht.DHT11(board.GP14)

test_motor = False

pwm16_motor1 = pwmio.PWMOut(board.GP16, frequency=1000)
pwm17_motor1 = pwmio.PWMOut(board.GP17, frequency=1000)
motor_1 = motor.DCMotor(pwm16_motor1, pwm17_motor1)
motor_1.decay_mode = (motor.SLOW_DECAY)

pwm15_ledfilament = pwmio.PWMOut(board.GP15, frequency=1000)
pwm11_ledfilament = pwmio.PWMOut(board.GP11, frequency=1000)
pwm10_ledfilament = pwmio.PWMOut(board.GP10, frequency=1000)

NEOPIXEL = board.GP22
NUM_PIXELS = 20
pixels = NeoPixelBackground(NEOPIXEL, NUM_PIXELS)
pixels.brightness = 0.15


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
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == '1':
        print('scenario 1 invoked')
        pass

################ Wifi Connection ################
try:
    if wifi.radio.ipv4_address is None:
        print("connecting to wifi")
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'),
                        os.getenv('CIRCUITPY_WIFI_PASSWORD'))
except Exception as e:
    print("Failed to connect to Wi-Fi: ", repr(e))
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    microcontroller.reset()
print(f"local address {wifi.radio.ipv4_address}")

aio_username = os.getenv('aio_username')
aio_key = os.getenv('aio_key')

################ Initialise MQTT ################
try:
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


print('sleeping before activation...')
time.sleep(5)
print('activated!')

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
        "ON": 2,
        "PREV_TIME": -1,
        "OBJECT": tof_sensor,
        "PRESENCE_VALUE": -1    # 0 for no human presence, 1 for human presence
    },
    {
        "ON": 4,
        "PREV_TIME": -1,
        "OBJECT": io
    }
]

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


################ Main program loop ################

while True:
    now = time.monotonic()

    # This section reads live data from sensors and sends them
    for sensor in SENSOR_LIST:
        if now >= sensor["PREV_TIME"] + sensor["ON"]:
            if type(sensor["OBJECT"]) is adafruit_bh1750.BH1750:
                sensor["PREV_TIME"] = now
                ################# TODO SEND DATA TO MQTT HERE #################
                print("%.2f Lux" % sensor["OBJECT"].lux)

            if type(sensor["OBJECT"]) is adafruit_dht.DHT11:
                sensor["PREV_TIME"] = now
                try:
                    temperature_c = sensor["OBJECT"].temperature
                    humidity = sensor["OBJECT"].humidity
                    if type(temperature_c) is None:
                        print('is none!!!')
                    else:
                        temperature_f = temperature_c * (9 / 5) + 32
                        ################# TODO SEND DATA TO MQTT HERE #################
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
                ################# TODO SEND DATA TO MQTT HERE #################
                print('Range: {}mm'.format(sensor["OBJECT"].range))
            
            if type(sensor["OBJECT"]) is IO_MQTT:
                sensor["PREV_TIME"] = now
                # Package up all the data and send it to MQTT
                ################# TODO SEND DATA TO MQTT HERE #################

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

    for light in LIGHT_LIST:
        if now >= light["PREV_TIME"] + light["ON"]:
            if light["FADE_DIR"] == True:
                # increase brightness
                light["PWM"] += 255
            elif light["FADE_DIR"] == False:
                # decrease brightness
                light["PWM"] -= 255
            
            # apply changes
            light["PIN"].duty_cycle = light["PWM"]
            light["PREV_TIME"] = now

            # change direction of fade
            if light["PWM"] < 0x0002:
                light["FADE_DIR"] = True
                # increase brightness
            elif light["PWM"] > 0xfff1:
                light["FADE_DIR"] = False
                # decrease brightness
            
    pixels.fill(rainbowio.colorwheel(supervisor.ticks_ms() // 16))
