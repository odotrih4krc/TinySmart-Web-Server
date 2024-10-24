import network
import socket
import time
from machine import Pin

# Wi-Fi credentials
SSID = 'your_wifi_ssid'  # Replace with your Wi-Fi SSID
PASSWORD = 'your_wifi_password'  # Replace with your Wi-Fi password

# Configure GPIO pins for LEDs
leds = [Pin(21, Pin.OUT), Pin(22, Pin.OUT), Pin(23, Pin.OUT)]

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connection
while not wlan.isconnected():
    print("Connecting to network...")
    time.sleep(1)

print("Connected to Wi-Fi")
print("IP Address:", wlan.ifconfig()[0])

# Create a socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Listening on", addr)

def serve_web_page():
    return """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <title>ESP32 LED Control</title>
    <style>
        body { text-align: center; padding: 20px; }
        .card { margin: 10px; }
        .navbar { margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-light bg-light">
        <a class="navbar-brand" href="#">
            <img src="https://via.placeholder.com/30" alt="Logo" class="d-inline-block align-top">
            TinySmart Dashboard
        </a>
    </nav>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">LIGHT 1</h5>
                        <button class="btn btn-primary" onclick="toggleLED(0)">Toggle LIGHT 1</button>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">LIGHT 2</h5>
                        <button class="btn btn-primary" onclick="toggleLED(1)">Toggle LIGHT 2</button>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">LIGHT 3</h5>
                        <button class="btn btn-primary" onclick="toggleLED(2)">Toggle LIGHT 3</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        function toggleLED(ledIndex) {
            fetch('/toggle?led=' + ledIndex)
                .then(response => response.text())
                .then(data => console.log(data));
        }
    </script>
</body>
</html>
"""

while True:
    # Accept a connection
    cl, addr = s.accept()
    print("Client connected from", addr)

    # Read the request
    request = cl.recv(1024)
    print("Request:", request)

    # Handle LED toggle
    if b'/toggle?led=' in request:
        led_index = int(request.split(b'led=')[1].split(b' ')[0])
        if 0 <= led_index < len(leds):
            leds[led_index].value(not leds[led_index].value())  # Toggle LED
            print(f'Toggled LED {led_index + 1}')

    # Prepare and send the web page
    response = serve_web_page()
    cl.send(response)
    cl.close()