# Main LCD 16x2 I2C - Forecast API Consume Python Script

import threading
import lcddriver
import datetime

import forecast

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()


def get_time():
    currentTime = datetime.datetime.now()
    return currentTime


# return currentTime.strftime("%d.%m %a %H:%M")


# display function
def print_lcd():
    global counter
    global weather
    global rate_info

    t = threading.Timer(1, print_lcd)
    t.start()

    print('Writing to display: ', counter)

    if counter == 0:
        weather = forecast.get_weather()
        rate_info = forecast.get_gold_rate()

    counter = counter + 1

    if counter == 60:
        counter = 0

    timeStr = str(get_time().time().strftime("%H:%M:%S"))
    weather_line = 'Temp:' + weather.get_temp() + ' ' + timeStr
    display.lcd_display_string(weather_line, 1)

    rate_line = 'G: ' + rate_info.get_gold22() + ' S: ' + rate_info.get_silver()
    display.lcd_display_string(rate_line, 2)

# main starts here

print('Test')

counter = 0

try:
    print_lcd()

except KeyboardInterrupt:
    print('Cleaning up !')
    display.lcd_clear();
