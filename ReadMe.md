# **GPS-Based Location Sharing Device Using ESP32**

## 1. **Introduction**

The aim of this project is to design a location-sharing device using the ESP32 microcontroller and a GPS module. The device retrieves the user’s current geographical coordinates (latitude and longitude) and sends this information via SMS using the Twilio API. This portable device can be used in various real-time tracking applications, such as personal safety, asset tracking, and remote monitoring.

## 2. **Project Components**

### 2.1 **ESP32 Microcontroller**
The ESP32 serves as the main control unit, managing GPS data acquisition and connecting to Wi-Fi for communication. Its low power consumption, integrated Wi-Fi and Bluetooth capabilities, and sufficient processing power make it ideal for this IoT-based project.
![esp32 cam](https://reversepcb.com/wp-content/uploads/2023/02/ESP32-CAM-camera-development-board.png)
### 2.2 **GPS Module (e.g., NEO-6M)**
The GPS module retrieves the device’s location in real-time by capturing satellite signals and converting them into latitude and longitude data. This data is parsed and processed by the ESP32 to generate a URL for Google Maps.

### 2.3 **Push Button**
A push button is used as an input trigger. When pressed, the ESP32 captures the GPS data and initiates the SMS-sending function.
![gps sensor](https://1.bp.blogspot.com/-jnz8MnX8YS0/X6zOwAqQogI/AAAAAAAAAfA/yO6UKmsAirMKwneOHm2IOO3p-Yv4gt6WACLcBGAsYHQ/s512/NEO-6M-GPS-Receiver-Module.jpg)
### 2.4 **Twilio API**
Twilio is an API used to send SMS messages over cellular networks. Using Twilio, the ESP32 sends an SMS with a Google Maps link, allowing the recipient to view the sender’s current location.

## 3. **System Design and Architecture**

The project follows a modular design with the following components:

1. **GPS Data Acquisition**: The ESP32 reads GPS data via UART, extracting relevant location information (latitude, longitude, satellite count, and timestamp).
2. **Location Parsing**: The GPS data is parsed to ensure accurate formatting and validation.
3. **Location Transmission**: Once a valid GPS fix is obtained, the ESP32 constructs a Google Maps URL using the latitude and longitude data.
4. **SMS Sending**: When the button is pressed, the Twilio API is used to send the Google Maps URL to a specified recipient via SMS.

The architecture allows for quick GPS updates, minimal power consumption, and reliable communication of the location data.

## 4. **Circuit Diagram**

The circuit connects the ESP32 microcontroller to the GPS module via the UART interface, and the push button is connected to one of the ESP32’s GPIO pins. The wiring setup is as follows:

- **GPS Module**: 
  - TX (GPS) → RX (ESP32, GPIO 14)
  - RX (GPS) → TX (ESP32, GPIO 16)
  - VCC and GND connected to the power and ground pins on ESP32.

- **Button**: Connected to GPIO 15 on the ESP32 with a pull-up resistor.
![circuit](https://www.electronicwings.com/storage/PlatformSection/TopicContent/475/description/GSP%20interface%20with%20NodeMCU.png)
## 5. **Software Implementation**

The software is written in MicroPython and consists of several key functions:

- **Wi-Fi Connection**: Connects to the specified Wi-Fi network to access the internet and Twilio API.
- **GPS Data Parsing**: Extracts latitude and longitude from the GPS module output and formats them.
- **Google Maps URL Generation**: Converts the latitude and longitude to a Google Maps link.
- **Twilio SMS API**: Uses the Twilio API to send the generated link as an SMS to a specified recipient.

## 6. **Challenges Faced**

### 6.1 **GPS Signal Reception**
Since GPS reception requires an open sky view, the device may struggle to obtain an accurate fix indoors or in dense urban areas. Adjustments were made to increase the timeout duration to allow for reliable data acquisition.

### 6.2 **Power Consumption**
The ESP32 and GPS module are power-intensive, especially when actively transmitting data. Low-power modes or power-saving modifications could be explored in future iterations to increase battery efficiency.

### 6.3 **Network Connectivity Issues**
Occasionally, network connectivity could be an issue, especially in remote areas with poor Wi-Fi coverage. A solution could be to add GSM capabilities for cellular data, allowing more versatile usage.

## 7. **Applications**

This GPS-based location-sharing device can be used in various applications:

- **Personal Safety**: Individuals can use it to share their real-time location with friends or family.
- **Asset Tracking**: Businesses can use the device for real-time tracking of vehicles or assets.
- **Emergency Situations**: It could be used to send location details in emergencies, especially when quick and easy tracking is crucial.

## 8. **Future Improvements**

- **Battery Optimization**: Implement low-power modes on the ESP32 and GPS module to extend battery life.
- **Improved Connectivity**: Integrate GSM/GPRS functionality to eliminate reliance on Wi-Fi.
- **Enhanced Security**: Add authentication to prevent unauthorized access to the device’s SMS functionality.
