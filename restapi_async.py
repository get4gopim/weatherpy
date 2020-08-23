# Main LCD 16x2 I2C - Forecast API Consume Python Script

import threading
import asyncio
import json

import datetime

import lcddriver

import WeatherInfo
import RateInfo

from aiohttp import ClientSession
from collections import namedtuple

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

def get_time():
    return datetime.datetime.now()

weather_url = 'http://localhost:8080/forecast/weather'
gold_rate_url = 'http://localhost:8080/forecast/gold'

# call async rest call to get weather details
async def get_weather():
    global weather
    async with ClientSession() as s, s.get(weather_url) as response:
        ret = await response.read()
        x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        print(x)
        weather = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asOf, x.currentCondition, x.location)
        return weather

# call async rest call to get gold rate detail
async def get_gold_rate():
    global rate_info
    async with ClientSession() as s, s.get(gold_rate_url) as response:
        ret = await response.read()
        x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        print(x)
        rate_info = RateInfo.RateInfo(x.goldRate22, x.goldRate24, x.silver)
        return rate_info

# display function
def print_lcd():
    global counter
    global line1, line2, line3, line4

    t = threading.Timer(1, print_lcd)
    t.start()

    line1 = get_time().strftime("%d.%m  %a  %H:%M:%S")
    line2 = str(weather.get_condition()) + ' ' + str(weather.get_temp()) + 'c'
    #line3 = weather.get_location()[0:20]
    #line4 = 'Gold   ' + rate_info.get_gold22() + ' Silv ' + rate_info.get_silver()
    line3 = 'Gold   Rate   ' + rate_info.get_gold22()
    line4 = 'Silver Rate   ' + rate_info.get_silver()

    #print('Writing to display: ', counter)

    display.lcd_display_string(line1, 1)

    # Every reset counter clear and refresh the data lines
    if counter == 0:
        display.lcd_clear();
        display.lcd_display_string(line1, 1)
        display.lcd_display_string(line2, 2)
        display.lcd_display_string(line3, 3)
        display.lcd_display_string(line4, 4)

    # Refresh the data every 5 mins (300 seconds once)
    if counter == 300:
        counter = 0
        asyncio.run(get_weather())
        # Query Gold Rate only in between 9 AM to 5 PM and not on SUNDAYS
        if (datetime.datetime.today().weekday() != 6 and
                (9 <= get_time().hour <= 17)):
            asyncio.run(get_gold_rate())

    counter = counter + 1

# main starts here
if __name__ == '__main__':
    print('Display 16x4 LCD Module Starts')
    counter = 0
    try:
        asyncio.run(get_weather())
        asyncio.run(get_gold_rate())
        print_lcd()

    except KeyboardInterrupt:
        print('Cleaning up !')
        display.lcd_clear()
