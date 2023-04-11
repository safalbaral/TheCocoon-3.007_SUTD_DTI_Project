import os
import time
import ipaddress
import wifi
import socketpool
import busio
import board
import microcontroller
import time
import board
import digitalio

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#  connect to network
ssid = os.getenv('CIRCUITPY_WIFI_SSID')
print()
print(f"Connecting to WiFi {ssid}")


ping_address = ipaddress.ip_address("192.168.1.1")

#wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)

#  connect to your SSID
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)

print("Connected to WiFi")

### Have to set static ip ideally but android hotspots are wack and don't have a stable gateway so things get complicated, so for now ip isn't stable
gateway = wifi.radio.ipv4_gateway
netmask = ipaddress.IPv4Address("255.255.255.0")
ipv4 = wifi.radio.ipv4_address

print(f'gateway{gateway}, netmask{netmask}, ipv4{ipv4}')#
#print(f'gateway{type(gateway)}, netmask{type(netmask)}, ipv4{type(ipv4)}')
ipv4 = ipaddress.IPv4Address('172.16.20.2')

#wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

@server.route("/example", HTTPMethod.GET)
def route_func(request):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send("<h1>Hello, ooga booga.</h1>")

#  route default static IP
@server.route("/test", method=HTTPMethod.GET)
def base(request: HTTPRequest):
    print('test route accessed.')
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send("<h1>Hello, ooga booga.</h1>")

#  if a button is pressed on the site
@server.route("/", method=HTTPMethod.POST)
def buttonpress(request: HTTPRequest):
    print('Button pressed')
    raw_text = request.raw_request.decode("utf8")
    if '1' or '2' in raw_text:
        led.value = True
        time.sleep(0.2)
        led.value = False
        time.sleep(0.2)



print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()

clock = time.monotonic()
while True:
    try:
        #  every 30 seconds, ping server & update temp reading
        if (clock + 30) < time.monotonic():
            if wifi.radio.ping(ping_address) is None:
                print("lost connection")
            else:
                print("connected")
            clock = time.monotonic()
        #  poll the server for incoming/outgoing requests
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue



