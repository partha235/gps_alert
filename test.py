import network
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, UART
import time, utime

try:
    from bps_cre import *     
except:
    pass

# Replace these with your Adafruit IO credentials
ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_IO_USERNAME = ada_user
ADAFRUIT_IO_KEY = ada_tok
FEED_NAME = "location-alert"  # Make sure this matches your feed name exactly

mqtt_client_id      = bytes('bps', 'utf-8')

# Wi-Fi credentials
SSID = bps_ssid
PASSWORD = bps_passw

# Predefined fallback GPS coordinates (as floats, not strings)
DEFAULT_LATITUDE = 11.384609
DEFAULT_LONGITUDE = 79.697655

# GPS module setup
gps = UART(1, baudrate=9600, tx=17, rx=16, timeout=500)

# Declare latitude and longitude as global variables
latitude = None
longitude = None

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected! IP address:", wlan.ifconfig()[0])

# GPS Parsing Function
def getGPS(gpsModule):
    global latitude, longitude, FIX_STATUS, TIMEOUT, satellites, GPStime
    
    timeout = time.time() + 5  # Timeout after 5 seconds
    while True:
        line = gpsModule.readline()
        if line:
            buff = str(line)
            parts = buff.split(',')
            
            if parts[0] == "b'$GPGGA" and len(parts) == 15:  # Check for valid GPS sentence
                if all(parts[1:8]):  # Ensure necessary parts are present
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
                    FIX_STATUS = True
                    break
        if time.time() > timeout:
            TIMEOUT = True
            break
        utime.sleep_ms(10)

# Convert GPS coordinates to degrees
def convertToDegree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat / 100) 
    nexttwodigits = RawAsFloat - float(firstdigits * 100)
    
    Converted = float(firstdigits + nexttwodigits / 60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)

def setup_mqtt():
    client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_IO_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)
    client.connect()
    return client

def publish_location(client, latitude, longitude):
    # Format the data as a CSV string: "lat,lon"
    payload = f"22.56,{latitude},{longitude}"
    print("payload = ", payload)
    print(type(payload))
    print("Publishing to Adafruit IO:", payload)
    try:
        topic = f"{ADAFRUIT_IO_USERNAME}/feeds/{FEED_NAME}/csv"
        client.publish(topic, payload)
        print("Data published successfully!")
    except Exception as e:
        print("Error publishing data:", e)

def main():
    global latitude, longitude  # Ensure latitude and longitude are accessible here
    connect_wifi()
    mqtt_client = setup_mqtt()
    
    while True:
        print("Fetching GPS data...")
        getGPS(gps)  # Ensure GPS data is updated
        
        if latitude is None or longitude is None:  # If no GPS data is available
            print("No GPS data available. Using fallback location.")
            latitude = DEFAULT_LATITUDE
            longitude = DEFAULT_LONGITUDE
        
        print(f"Location: Latitude={latitude}, Longitude={longitude}")
        publish_location(mqtt_client, latitude, longitude)
        time.sleep(30)

if __name__ == "__main__":
    main()
