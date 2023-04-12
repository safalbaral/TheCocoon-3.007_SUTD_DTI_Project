"""
Button example for Pico. Prints message to serial console when button is pressed.

REQUIRED HARDWARE:
* Button switch on pin GP13.
"""
import time
import board
import digitalio
import busio
import adafruit_displayio_ssd1306
import displayio
import terminalio

from adafruit_display_text.label import Label

displayio.release_displays()

button = digitalio.DigitalInOut(board.GP18)
i2c = busio.I2C(board.GP17, board.GP16)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
#display_bus = displayio.I2CDisplay(i2c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Make the display context
screen_group = displayio.Group()
title_label = Label(terminalio.FONT, text="Detection State")
title_label.x = 0
title_label.y = 10
screen_group.append(title_label)

state_label = Label(terminalio.FONT, text='Starting Radar...')
state_label.x = 0
state_label.y = 30
screen_group.append(state_label)
display.show(screen_group)

while True:
    if button.value:
        state_label.text ='Radar Detected'
        print('Detected')
    else:
        state_label.text = 'Radar Not Detected'
        print('Not Detected')
    time.sleep(0.5)
