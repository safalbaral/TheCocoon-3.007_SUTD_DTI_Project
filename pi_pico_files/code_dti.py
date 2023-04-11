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
from adafruit_motor import motor
from pioasm_neopixel_bg import NeoPixelBackground
import rainbowio
import supervisor

print('sleeping before activation...')
time.sleep(5)
print('activated!')

i2c = busio.I2C(scl=board.GP13, sda=board.GP12, frequency=50000)
light_sensor = adafruit_bh1750.BH1750(i2c)

dht_sensor = adafruit_dht.DHT11(board.GP14)

test_motor = False

pwm16_motor1 = pwmio.PWMOut(board.GP16, frequency=1000)
pwm17_motor1 = pwmio.PWMOut(board.GP17, frequency=1000)
motor_1 = motor.DCMotor(pwm16_motor1, pwm17_motor1)
motor_1.decay_mode = (motor.SLOW_DECAY)

pwm11_ledfilament = pwmio.PWMOut(board.GP11, frequency=1000)
pwm10_ledfilament = pwmio.PWMOut(board.GP10, frequency=1000)

NEOPIXEL = board.GP22
NUM_PIXELS = 20
pixels = NeoPixelBackground(NEOPIXEL, NUM_PIXELS)
pixels.brightness = 0.15

SENSOR_LIST = [
    {
        "ON": 2,
        "OFF": 2,
        "PREV_TIME": -1,
        "VALUE": light_sensor
    },
    {
        "ON": 2,
        "OFF": 2,
        "PREV_TIME": -1,
        "VALUE": dht_sensor
    }
]

MOTOR_LIST = [
    {
        "ON": 5,
        "OFF": 5,
        "PREV_TIME": -1,
        "MOTOR": motor_1
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
    }
]

while True:
    now = time.monotonic()
    # This line of code demonstrates BH1750 light intensity sensor readings
    for sensor in SENSOR_LIST:
        if now >= sensor["PREV_TIME"] + sensor["OFF"]:
            if type(sensor["VALUE"]) is adafruit_bh1750.BH1750:
                sensor["PREV_TIME"] = now
                print("%.2f Lux" % sensor["VALUE"].lux)

            if type(sensor["VALUE"]) is adafruit_dht.DHT11:
                sensor["PREV_TIME"] = now
                try:
                    temperature_c = sensor["VALUE"].temperature
                    humidity = sensor["VALUE"].humidity
                    if type(temperature_c) is None:
                        print('is none!!!')
                    else:
                        temperature_f = temperature_c * (9 / 5) + 32
                        print(
                            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                                temperature_f, temperature_c, humidity
                            )
                        )
                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    print('DHT error: ', error.args[0])
                    pass
                except Exception as error:
                    print('DHT related error: ', error.args[0])
                    pass


    # This section of code demonstrates DHT11 temp/humidity sensor readings
    # try:
    #     # Print the values to the serial port
    #     temperature_c = dht_sensor.temperature
    #     temperature_f = temperature_c * (9 / 5) + 32
    #     humidity = dht_sensor.humidity
    #     print(
    #         "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
    #             temperature_f, temperature_c, humidity
    #         )
    #     )
    # except RuntimeError as error:
    #     # Errors happen fairly often, DHT's are hard to read, just keep going
    #     print('DHT error: ', error.args[0])
    #     continue
    # except Exception as error:
    #     dht_sensor.exit()
    #     raise error

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
