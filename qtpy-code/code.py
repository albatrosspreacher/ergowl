{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import wifi\
import adafruit_requests\
import gc\
import socketpool\
import time\
import board\
import busio\
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX\
\
# WiFi configuration\
WIFI_SSID = os.getenv('CIRCUITPY_WIFI_SSID')\
WIFI_PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD')\
\
# Define HTTP server port\
HTTP_SERVER_PORT = 80\
\
# Initialize I2C bus and LSM6DSOX sensor\
i2c = busio.I2C(board.SCL1, board.SDA1)\
sensor = LSM6DSOX(i2c)\
\
# Calibration values for reference posture\
calibration_values = \{'x': 0, 'y': 0, 'z': 0\}\
\
# Thresholds for detecting bad posture\
thresholds = \{'x': 0.5, 'y': 0.5, 'z': 9.8\}  # Adjust as needed\
\
def calibrate_sensor():\
    # Perform sensor calibration to determine reference posture\
    total_samples = 100\
    sum_acceleration = \{'x': 0, 'y': 0, 'z': 0\}\
\
    print("Calibrating sensor...")\
    for _ in range(total_samples):\
        acceleration = sensor.acceleration\
        sum_acceleration['x'] += acceleration[0]\
        sum_acceleration['y'] += acceleration[1]\
        sum_acceleration['z'] += acceleration[2]\
        time.sleep(0.01)\
\
    calibration_values['x'] = sum_acceleration['x'] / total_samples\
    calibration_values['y'] = sum_acceleration['y'] / total_samples\
    calibration_values['z'] = sum_acceleration['z'] / total_samples\
\
    print("Calibration complete.")\
\
def is_bad_posture(acceleration):\
    # Check if the posture is bad based on thresholds\
    delta_x = abs(acceleration[0] - calibration_values['x'])\
    delta_y = abs(acceleration[1] - calibration_values['y'])\
    delta_z = abs(acceleration[2] - calibration_values['z'])\
\
    if delta_x > thresholds['x'] or delta_y > thresholds['y'] or delta_z > thresholds['z']:\
        return True\
    else:\
        return False\
\
# Initialize WiFi connection\
print("Connecting to WiFi...")\
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)\
while not wifi.radio.ipv4_address:\
    pass\
print("Connected to WiFi.")\
print("IP Address:", wifi.radio.ipv4_address)\
\
# Initialize socket pool and requests session\
pool = socketpool.SocketPool(wifi.radio)\
requests = adafruit_requests.Session(pool)\
\
# Create a server socket\
server_socket = pool.socket()\
server_socket.bind(('0.0.0.0', HTTP_SERVER_PORT))\
server_socket.listen(1)\
\
print("HTTP server is running on \{\}:\{\}".format(wifi.radio.ipv4_address, HTTP_SERVER_PORT))\
\
send_posture_data = False\
\
# Serve requests indefinitely\
try:\
    while True:\
        # Accept incoming connection\
        client_socket, client_address = server_socket.accept()\
        print("Connection from:", client_address)\
\
        # Receive the request from the client\
        buffer = bytearray(1024)  # Create a buffer to receive data\
        bytes_received = client_socket.recv_into(buffer, 1024)  # Receive data into the buffer\
        request = buffer[:bytes_received].decode('utf-8').strip()  # Decode received bytes to string\
        print(request)\
        # Split the request based on the blank line\
        request_parts = request.split("\\r\\n\\r\\n", 1)\
\
        # Extract the HTTP body from the second part of the split\
        if len(request_parts) > 1:\
            http_body = request_parts[1]\
            print("HTTP Body:", http_body)\
        else:\
            print("No HTTP Body found in the request.")\
        if http_body == "connect":\
            response = "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nConnected\\r\\n"\
            client_socket.sendall(response.encode('utf-8'))\
        elif http_body == "configure":\
            calibrate_sensor()\
            response = "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\Configuration\\r\\n"\
            client_socket.sendall(response.encode('utf-8'))\
        elif http_body == "posture":\
            posture = is_bad_posture(sensor.acceleration)\
            response = "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nBad Posture: \{\}\\r\\n".format(posture)\
            client_socket.sendall(response.encode('utf-8'))\
            send_posture_data = True\
        else:\
            response = "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nUnknown\\r\\n"\
            client_socket.sendall(response.encode('utf-8'))\
\
        while send_posture_data:\
            posture = is_bad_posture(sensor.acceleration)\
            print(posture)\
            response = "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nBad Posture: \{\}\\r\\n".format(posture)\
            client_socket.sendall(response.encode('utf-8'))\
            time.sleep(10)\
        \
        # Close the client socket\
        client_socket.close()\
\
        # Delay to prevent overwhelming the system\
        time.sleep(0.1)\
\
finally:\
    # Close the server socket\
    server_socket.close()\
\
}