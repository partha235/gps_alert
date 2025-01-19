import network
import ntptime
from machine import Pin, SoftI2C
import gc
from utime import sleep_ms, localtime, mktime
import ssd1306

# Free up memory
gc.collect()

# Wi-Fi Credentials
SSID = "bps_wifi"     # Your network SSID
PASSWORD = "sagabps@235"  # Your network password

# I2C and OLED Display
i2c = SoftI2C(scl=Pin(13), sda=Pin(12)) 
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Time Zone Offset (IST: UTC+5:30 = 19800 seconds)
TIME_ZONE_OFFSET = 5 * 3600 + 30 * 60

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Get Local Time with Time Zone Adjustment
def get_local_time():
    utc_time = localtime()  # Get UTC time
    local_time = mktime(utc_time) + TIME_ZONE_OFFSET  # Apply offset
    return localtime(local_time)  # Convert back to tuple

# Display Time on OLED
def display_time(adjusted_time):
    date = f"{adjusted_time[2]:02}/{adjusted_time[1]:02}/{adjusted_time[0]}"
    time_str = f"{adjusted_time[3]:02}:{adjusted_time[4]:02}:{adjusted_time[5]:02}"
    oled.fill(0)
    oled.text("Date:", 0, 0)
    oled.text(date, 0, 10)
    oled.text("Time:", 0, 30)
    oled.text(time_str, 0, 40)
    oled.show()

# Main Loop
try:
    connect_wifi()
    while True:
        try:
            ntptime.settime()  # Sync time with NTP server
            adjusted_time = get_local_time()
            print("NTP Time:", adjusted_time)
            display_time(adjusted_time)
        except Exception as e:
            print("Error:", e)
        sleep_ms(5000)  # Update every 5 seconds
except KeyboardInterrupt:
    print("Program stopped.")
