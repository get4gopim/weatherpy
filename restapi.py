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

    if counter == 10:
        counter = 0
        weather = forecast.get_weather()
        if datetime.datetime.today().weekday() != 6:
            rate_info = forecast.get_gold_rate()
        display.lcd_clear();

    counter = counter + 1

    #timeStr = str(get_time().time().strftime("%H:%M:%S"))
    #timeStr = get_time().strftime("%d.%b.%y %a %H:%M")
    line1 = get_time().strftime("%d.%m %a %H:%M:%S")
    line2 = str(weather.get_condition()) + '  ' + str(weather.get_temp()) + 'c'
    #line3 = 'Gold ' + rate_info.get_gold22() + ' Sil ' + rate_info.get_silver()
    line3 = 'Gold Rate      ' + rate_info.get_gold22()
    line4 = 'Silver Rate    ' + rate_info.get_silver()
    #line4 = weather.get_location()[0:20]

    display.lcd_display_string(line1, 1)
    display.lcd_display_string(line2, 2)
    display.lcd_display_string(line3, 3)
    display.lcd_display_string(line4, 4)


# main starts here

print('Test')

counter = 0

try:
    weather = forecast.get_weather()
    rate_info = forecast.get_gold_rate()
    print_lcd()

except KeyboardInterrupt:
    print('Cleaning up !')
    display.lcd_clear();
