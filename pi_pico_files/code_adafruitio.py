# pyright: reportShadowedImports=false
import time
import board
import busio
import microcontroller
import adafruit_scd30
import os
import ssl
import wifi
import socketpool
from adafruit_io.adafruit_io import IO_MQTT
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Define callback functions which will be called when certain events happen.
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

def on_calib_msg(client, topic, message):
    # Method called whenever user/feeds/cornmen.calib has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == 'OK' or message == 'NOK':
        # acknowledgement messages should not affect anything
        pass
    elif is_int(message):
        calib_amount = int(message)
        time.sleep(1)
        for sensor in scd_sensors:
            sensor.forced_recalibration_reference = calib_amount
        print('Calibration complete, calibrated to:', calib_amount)
        try:
            # publish OK message
            io.publish('cornmen.calib', 'OK')
        except Exception as e:
            print('Acknowledgement for calibration publish failed!')
    else:
        io.publish('cornmen.calib', 'NOK')
        print("Calibration amount is not float!")







time.sleep(5)  # Wait for startup
print('-----------------------------------')

def is_int(element: any) -> bool:
    if element is None:
        return False
    try:
        int(element)
        return True
    except ValueError:
        return False

scd_sensors: list[adafruit_scd30.SCD30] = []

# init i2c and sensor for sanity check
try:
    i2c1 = busio.I2C(scl=board.GP3, sda=board.GP2, frequency=50000)
    scd_sensors.append(adafruit_scd30.SCD30(i2c1))
    scd_sensors[0].self_calibration_enabled = False
except Exception as e:
    print('Failed to connect to CO2 sensor 0: ', repr(e))
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    microcontroller.reset()

try:
    i2c2 = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=50000)
    scd_sensors.append(adafruit_scd30.SCD30(i2c2))
    scd_sensors[1].self_calibration_enabled = False
except Exception as e:
    print('Failed to connect to CO2 sensor 1: ', repr(e))

if len(scd_sensors) <= 0:
    print('Failed to connect to any CO2 sensor')
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    microcontroller.reset()

# connect to wifi
try:
    if wifi.radio.ipv4_address is None:
        print("connecting to wifi")
        # wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'),
        #                 os.getenv('CIRCUITPY_WIFI_PASSWORD'))
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID1'))
except Exception as e:
    print("Failed to connect to Wi-Fi: ", repr(e))
    print("Resetting microcontroller in 30 seconds")
    time.sleep(30)
    microcontroller.reset()

print(f"local address {wifi.radio.ipv4_address}")

aio_username = os.getenv('aio_username')
aio_key = os.getenv('aio_key')

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
    io.add_feed_callback("cornmen.calib", on_calib_msg)
    io.connect()
    print("connected to io")
    # Setup subscribes here
    io.subscribe("cornmen.calib")
except Exception as e:
    print("Error in network setup:\n", repr(e))
    print("Resetting microcontroller in 20 seconds")
    time.sleep(20)
    microcontroller.reset()

print('Connected to feeds')

feed_names = ['cornmen.scd30-temp', 'cornmen.scd30-hum', 'cornmen.scd30-co2', 'cornmen.scd30-co2-2']
stored_data = {'co21': [], 'co22': [], 'temp': [], 'hum': []}

clock = 0
error_count = 0

while True:
    try:
        # ping adafruit MQTT. known bug that this will be blocking and cause delays, so account for it accordingly
        io.loop()
        
        # when the clock runs out, send the data (while this is 150, it is actually 300 seconds due to bug above)
        if clock > 150:
            if len(stored_data['temp']) > 0 and len(stored_data['hum']) > 0:
                data = [sum(stored_data['temp'])/len(stored_data['temp']),
                        sum(stored_data['hum'])/len(stored_data['hum'])]

                # check which sensor has data (length > 0)
                if len(stored_data['co21']) > 0:
                    # first sensor has data
                    data.append(sum(stored_data['co21'])/len(stored_data['co21']))
                if len(stored_data['co22']) > 0:
                    # second sensor has data, send both data!
                    data.append(sum(stored_data['co22'])/len(stored_data['co22']))
                
                for z in range(len(data)):
                    print('sending: ', feed_names[z], data[z])
                    try:
                        io.publish(feed_names[z], data[z])
                    except Exception as e:
                        print('Publish failed!')
                        raise e
                    print("sent: %0.1f" % data[z])
                    time.sleep(1)
                # successful send, reset clock and error
                clock = 0
                error_count = 0
            else:
                print('NO data from temperature! Is first sensor connected??')
                error_count += 1

        # store data for averaging later
        if clock % 5 == 0:
            print(clock)

            sensors_n = len(scd_sensors)
            
            for index, sensor in enumerate(scd_sensors):
                if index == 0 and sensor.data_available:
                    stored_data['co21'].append(scd_sensors[0].CO2)
                    stored_data['temp'].append(scd_sensors[0].temperature)
                    stored_data['hum'].append(scd_sensors[0].relative_humidity)

                    # dequeue extra data if it gets too big
                    if len(stored_data['co21']) >= 30:
                        stored_data['co21'].pop(0)
                    if len(stored_data['temp']) >= 30:
                        stored_data['temp'].pop(0)
                    if len(stored_data['hum']) >= 30:
                        stored_data['hum'].pop(0)
                elif index == 1 and sensor.data_available:
                    stored_data['co22'].append(scd_sensors[1].CO2)

                    # dequeue extra data if it gets too big
                    if len(stored_data['co22']) >= 30:
                        stored_data['co22'].pop(0)
        # increment clock no matter what
        clock += 1
    # pylint: disable=broad-except
    # any errors, reset Pico W
    except Exception as e:
        error_count += 1
        print("Error in main program loop:\n", repr(e))
        if error_count > 3:
            print("Resetting microcontroller in 20 seconds")
            time.sleep(20)
            error_count = 0
            microcontroller.reset()
        else:
            # set a 10 second delay and reattempt transmit
            clock = 290
    #  delay
    time.sleep(1)
