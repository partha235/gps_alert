from machine import Pin,SoftI2C
import ssd1306

#You can choose any other combination of I2C pins
i2c = SoftI2C(scl=Pin(12), sda=Pin(13)) 
print(i2c.scan())
print("hi")
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)                                                                                                        
oled.text('Saga', 0, 0)
oled.show()