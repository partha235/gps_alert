from machine import Pin, UART
import network
import gc
import utime
import time
try:
    import urequests as requests
except:
    import requests
from umqtt.simple import MQTTClient
try:
    from bps_cre import *     
except:
    pass

# Wi-Fi Credentials
ssid = bps_ssid     # your network/hotspot/ssid name.
password = bps_passw    # your network/hotspot/ssid password.

# Twilio API Credentials
account_sid = twilio_sid
auth_token = twilio_tok
recipient_num = '+919488790964'
sender_num = twilio_num

# Adafruit IO Credentials
ADAFRUIT_IO_USERNAME = ADAFRUIT_AIO_USERNAME
ADAFRUIT_IO_KEY = ADAFRUIT_AIO_KEY
FEED_NAME = "location-alert"  # Feed name to store location data

# GPS module setup
gpsModule = UART(1, 9600)
gpsModule.init(9600, bits=8, parity=None, stop=1, rx=14, tx=16)

# Button Setup
but = Pin(15, Pin.IN, Pin.PULL_UP)

# Predefined fallback GPS coordinates (as floats, not strings)
DEFAULT_LATITUDE = 11.384609
DEFAULT_LONGITUDE = 79.697655

# Global variables for GPS data
latitude = ""
longitude = ""
satellites = ""
GPStime = ""

gc.collect()

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        pass
    print('Connection successful')
    print(station.ifconfig())

# Get GPS Data
def getGPS(gpsModule):
    global latitude, longitude, satellites, GPStime
    timeout = time.time() + 10
    while True:
        line = gpsModule.readline()
        if line:
            buff = str(line)
            parts = buff.split(',')
            if parts[0] == "b'$GPGGA" and len(parts) == 15:
                if all(parts[1:8]):  # Check if all necessary parts are present
                    print(buff)
                    latitude = convertToDegree(parts[2])
                    if parts[3] == 'S':
                        latitude = -latitude
                    longitude = convertToDegree(parts[4])
                    if parts[5] == 'W':
                        longitude = -longitude
                    satellites = parts[7]
                    GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                    message = f"https://www.google.com/maps?q={latitude},{longitude}&z=17&hl=en"
                    print(message)
                    return True
        if time.time() > timeout:
            print("GPS Timeout. Using fallback location.")
            return False
        utime.sleep_ms(500)

# Convert raw GPS data to degrees
def convertToDegree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat / 100)
    nexttwodigits = RawAsFloat - float(firstdigits * 100)
    Converted = float(firstdigits + nexttwodigits / 60.0)
    Converted = '{0:.6f}'.format(Converted)
    return str(Converted)

# Send SMS using Twilio API
def send_sms(recipient, sender, message, auth_token, account_sid):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = f"To={recipient}&From={sender}&Body={message}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    print("Trying to send SMS with Twilio")
    
    response = requests.post(url, data=data, auth=(account_sid, auth_token), headers=headers)
    
    if response.status_code == 201:
        print("SMS sent!")
    else:
        print(f"Error sending SMS: {response.text}")
    response.close()

# Set up MQTT connection to Adafruit IO
def setup_mqtt():
    client = MQTTClient("ESP32", "io.adafruit.com", user=ADAFRUIT_IO_USERNAME, password=ADAFRUIT_IO_KEY)
    client.connect()
    return client

# Publish location to Adafruit IO
def publish_location(client, latitude, longitude):
    # Format the data as a CSV string: "lat,lon"
    payload = f"{latitude},{longitude}"
    print(f"Publishing to Adafruit IO: {payload}")
    try:
        topic = f"{ADAFRUIT_IO_USERNAME}/feeds/{FEED_NAME}"
        client.publish(topic, payload.encode())
        print("Data published successfully!")
    except Exception as e:
        print("Error publishing data:", e)

# Main loop
def main():
    connect_wifi(ssid, password)
    mqtt_client = setup_mqtt()

    while True:
        # Try to get GPS data
        gps_available = getGPS(gpsModule)
        
        if gps_available:
            print(f"Latitude: {latitude}, Longitude: {longitude}, Satellites: {satellites}")
        else:
            print("No GPS data found. Using fallback location.")
            latitude = DEFAULT_LATITUDE
            longitude = DEFAULT_LONGITUDE
        
        # Send SMS with location if button is pressed
        if not but.value():
            message = f"Location: https://www.google.com/maps?q={latitude},{longitude}"
            send_sms(recipient_num, sender_num, message, auth_token, account_sid)
            print("Sent SMS with location!")
        
        # Publish location to Adafruit IO every 30 seconds
        publish_location(mqtt_client, latitude, longitude)
        
        # Sleep for a while before checking again
        time.sleep(30)

# Run the main function
if __name__ == "__main__":
    main()

