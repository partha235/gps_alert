import network
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, UART
import time

try:
    from bps_cre import *     
except:
    pass

# Replace these with your Adafruit IO credentials
ADAFRUIT_IO_USERNAME = ADAFRUIT_AIO_USERNAME
ADAFRUIT_IO_KEY = ADAFRUIT_AIO_KEY
FEED_NAME = "location-alert"  # Make sure this matches your feed name exactly

# Wi-Fi credentials
SSID = "Nokiabps"
PASSWORD = "bps12345"

# Predefined fallback GPS coordinates (as floats, not strings)
DEFAULT_LATITUDE = 11.384609
DEFAULT_LONGITUDE = 79.697655

# GPS module setup
gps = UART(1, baudrate=9600, tx=17, rx=16, timeout=500)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected! IP address:", wlan.ifconfig()[0])

def parse_gps():
    timeout = time.time() + 5
    while time.time() < timeout:
        line = gps.readline()
        if line and b"GPGGA" in line:
            try:
                parts = line.decode('utf-8').split(",")
                if len(parts) > 5 and parts[2] and parts[4]:
                    latitude = convert_to_degrees(parts[2], parts[3])
                    longitude = convert_to_degrees(parts[4], parts[5])
                    return float(latitude), float(longitude)
            except:
                pass
    return None, None

def convert_to_degrees(raw, direction):
    try:
        raw_float = float(raw)
        degrees = int(raw_float / 100)
        minutes = raw_float - degrees * 100
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees
    except:
        return None

def setup_mqtt():
    client = MQTTClient("ESP32", "io.adafruit.com", user=ADAFRUIT_IO_USERNAME, password=ADAFRUIT_IO_KEY)
    client.connect()
    return client

def publish_location(client, latitude, longitude):
    # Format the data as a CSV string: "lat,lon"
    payload = f"{latitude},{longitude}"
    print("Publishing to Adafruit IO:", payload)
    try:
        topic = f"{ADAFRUIT_IO_USERNAME}/feeds/{FEED_NAME}"
        client.publish(topic, str(payload).encode())
        print("Data published successfully!")
    except Exception as e:
        print("Error publishing data:", e)

def main():
    connect_wifi()
    mqtt_client = setup_mqtt()
    
    while True:
        print("Fetching GPS data...")
        latitude, longitude = parse_gps()
        
        if latitude is None or longitude is None:
            print("No GPS data available. Using fallback location.")
            latitude = DEFAULT_LATITUDE
            longitude = DEFAULT_LONGITUDE
        
        print(f"Location: Latitude={latitude}, Longitude={longitude}")
        publish_location(mqtt_client, latitude, longitude)
        time.sleep(30)

if __name__ == "__main__":
    main()
