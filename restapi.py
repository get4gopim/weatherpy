# Main LCD 16x2 I2C - Forecast API Consume Python Script

import threading
import lcddriver
import datetime

import forecast

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

# display function
def print_lcd():
        t = threading.Timer(60, print_lcd) # every x seconds call printLcd method
        t.start()
        # Actual Thread
        weather = forecast.get_weather()
        rate_info = forecast.get_gold_rate()

        #print ('Writing to display')

        #while True:
        timeStr = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
        weather_line = 'Temp:' + weather.get_temp() + '' + timeStr
        display.lcd_display_string(weather_line, 1)

        rate_line = 'Gold Rate: ' + rate_info.get_gold22()
        display.lcd_display_string(rate_line, 2)


# main starts here

print ('Test')

try:
	print_lcd()

except KeyboardInterrupt:
	print ('Cleaning up !')
	display.lcd_clear();
