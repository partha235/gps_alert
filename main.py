#  ver = SSS1YGNP2R92G5EBK46KAZQU
from machine import Pin, UART, SoftI2C
try:
  import urequests as requests
except:
  import requests
import network
import gc
import utime, time
try:
    from bps_cre import *     
except:
    pass

print("hi")
but=Pin(3,Pin.IN,Pin.PULL_UP)
L=Pin('LED',Pin.OUT)
gc.collect()

ssid=bps_ssid     # your network/hotspot/ssid name.
password=bps_passw    # your network/hotspot/ssid password.



# Your Account SID and Auth Token from twilio.com/console
account_sid = twilio_sid
auth_token = twilio_tok
recipient_num = '+919488790964'
sender_num = twilio_num

gpsModule = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
print(gpsModule)

buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""
print('connecting')
def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
   # print(station.scan())
    station.active(True)
    station.connect(ssid, password)
    L.on()
    time.sleep_ms(100)
    L.off()
    time.sleep_ms(100)
    L.on()
    time.sleep_ms(100)
    L.off()
    time.sleep_ms(100)
    while station.isconnected() == False:
        pass
    print('Connection successful')
    print(station.ifconfig())

connect_wifi(ssid, password)

def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime
    
    timeout = time.time() + 8 
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        parts = buff.split(',')
    
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                print(buff)
                
                latitude = convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    latitude = -latitude
                longitude = convertToDegree(parts[4])
                if (parts[5] == 'W'):
                    longitude = -longitude
                satellites = parts[7]
                GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                break
                
        if (time.time() > timeout):
            TIMEOUT = True
            break
        utime.sleep_ms(500)
        
def convertToDegree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)
    
def send_sms(recipient, sender,
             message, auth_token, account_sid):
      
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "To={}&From={}&Body={}".format(recipient,sender,message)
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(account_sid)
    
    print("Trying to send SMS with Twilio")
    
    response = requests.post(url,
                             data=data,
                             auth=(account_sid,auth_token),
                             headers=headers)
    
    if response.status_code == 201:
        print("SMS sent!")
    else:
        print("Error sending SMS: {}".format(response.text))
    
    response.close()



while True:
    
    getGPS(gpsModule)

    print("working")
    print('but = ',but.value())

    if(FIX_STATUS == True):
        print("Printing GPS data...")
        print(" ")
        print("Latitude: "+latitude)
        print("Longitude: "+longitude)
        print("Satellites: " +satellites)
        print("Time: "+GPStime)
        print("----------------------")
                
        FIX_STATUS = False
        if not but.value():
            message=f"I'm in danger, need help.MY location https://www.google.com/maps?q={latitude},{longitude}&z=17&hl=en"
            send_sms(recipient_num, sender_num, message, auth_token, account_sid)

    print("working")
    if(TIMEOUT == True):
        if not but.value():
            message=f"I'm in danger,help me https://www.google.com/maps?q=11.39432125437933,79.69728014705484&z=17&hl=en"
            send_sms(recipient_num, sender_num, message, auth_token, account_sid)
        print("No GPS data is found.")
        TIMEOUT = False

