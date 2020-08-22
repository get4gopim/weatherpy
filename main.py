# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import RateInfo
import WeatherInfo
import forecast
import threading
import datetime

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def get_time():
    currentTime = datetime.datetime.now()
    return currentTime

def print_lcd():
    global counter
    global weather
    global rate_info

    t = threading.Timer(1, print_lcd)
    t.start()

    print('Writing to display: ', counter)

    if counter == 5:
        weather = forecast.get_weather()
        rate_info = forecast.get_gold_rate()
        counter = 0

    counter = counter + 1

    #if counter == 60:
    #    counter = 0

    timeStr = str(get_time().time().strftime("%H:%M:%S"))
    weather_line = 'Temp:' + weather.get_temp() + ' ' + timeStr
    print (weather_line)

    rate_line = 'G: ' + rate_info.get_gold22() + ' S: ' + rate_info.get_silver()
    print (rate_line)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    counter = 0
    weather = forecast.get_weather()
    rate_info = forecast.get_gold_rate()

    print_hi('PyCharm')
    print_lcd()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

