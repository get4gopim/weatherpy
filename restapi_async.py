# Main LCD 16x2 I2C - Forecast API Consume Python Script
import random
import threading
import asyncio
import json
import logging
import os

import datetime
import time

import lcddriver

import WeatherInfo
import RateInfo
import FuelInfo

from aiohttp import ClientSession, ClientConnectorError
from collections import namedtuple

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

def get_time():
    return datetime.datetime.now()

weather_url = 'http://localhost:8080/forecast/weather'
gold_rate_url = 'http://localhost:8080/forecast/gold'
fuel_rate_url = 'http://localhost:8080/forecast/fuel'

# call async rest call to get weather details
async def get_weather():
    global weather
    try:
        async with ClientSession() as s, s.get(weather_url) as response:
            ret = await response.read()
            x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
            LOGGER.info(x)
            weather = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asOf, x.currentCondition, x.location)
            weather.set_error(None)
            update_weather_line()
            return weather
    except ClientConnectorError as ex:
        LOGGER.exception ('Unable to connect weather API', ex)
        weather = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "")
        weather.set_error(ex)

# call async rest call to get gold rate detail
async def get_gold_rate():
    global rate_info
    try:
        async with ClientSession() as s, s.get(gold_rate_url) as response:
            ret = await response.read()
            x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
            LOGGER.info(x)
            rate_info = RateInfo.RateInfo(x.goldRate22, x.goldRate24, x.silver, x.lastUpdateTime, x.date)
            rate_info.set_error(None)
            update_rate_line()
            return rate_info
    except ClientConnectorError as ex:
        LOGGER.exception ('Unable to connect rate API', ex)
        rate_info = RateInfo.RateInfo(0, 0, 0.0, "", "")
        rate_info.set_error(ex)

# call async rest call to get fuel details
async def get_fuel():
    global fuel_info
    try:
        async with ClientSession() as s, s.get(fuel_rate_url) as response:
            ret = await response.read()
            x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
            LOGGER.info(x)
            fuel_info = FuelInfo.FuelInfo(x.petrolPrice, x.dieselPrice, x.date, x.lastUpdatedTime)
            fuel_info.set_error(None)
            update_fuel_line()
            return fuel_info
    except ClientConnectorError as ex:
        LOGGER.exception ('Unable to connect weather API', ex)
        fuel_info = FuelInfo.FuelInfo(0, 0, "", "")
        fuel_info.set_error(ex)

# update display line weather strings
def update_weather_line():
    global line2

    temperature = str(weather.get_condition())[0:16]
    temperature = temperature.ljust(16, ' ')

    line2 = temperature + ' ' + str(weather.get_temp()) + 'c'

# update display line strings
def update_weather_line2():
    global line2

    # Make string 16 chars only
    line2 = str(weather.get_location())[0:20]

# update display line rate strings
def update_rate_line():
    global line3, line4

    # line4 = 'Gold   ' + rate_info.get_gold22() + ' Silv ' + rate_info.get_silver()
    line3 = 'Gold   Rate     ' + str(rate_info.get_gold22())
    line4 = 'Silver Rate    ' + str(rate_info.get_silver())

def update_fuel_line():
    global line3, line4

    # line4 = 'Petrol ' + fuel_info.get_petrol() + ' Disel' + fuel_info.get_diesel()
    line3 = 'Petrol Rate    ' + str(fuel_info.get_petrol())
    line4 = 'Diesel Rate    ' + str(fuel_info.get_diesel())

# display function
def print_lcd():
    global counter
    global line1

    t = threading.Timer(1, print_lcd)
    t.start()

    currentTime = get_time();
    line1 = currentTime.strftime("%d.%m  %a  %H:%M:%S")
    update_weather_line()
    update_fuel_line()

    #print('Writing to display: ', counter)

    change_every_x_secs = 5;
    rand_bool = random.choice([True, False])

    if currentTime.second % change_every_x_secs == 0:
        if rand_bool:
            update_weather_line2()
        else:
            update_weather_line()

        if weather.get_error() is None:
            display.lcd_display_string(line2, 2)

    display.lcd_display_string(line1, 1)

    # Every reset counter clear and refresh the data lines
    if counter == 0:
        display.lcd_clear();
        display.lcd_display_string(line1, 1)

        if rate_info.get_error() is None:
            display.lcd_display_string(line3, 3)
            display.lcd_display_string(line4, 4)

    # Refresh the data every 5 mins (300 seconds once)
    if counter == 300:
        counter = 0
        asyncio.run(get_weather())
        # Query Gold Rate only in between 9 AM to 5 PM and not on SUNDAYS
        if (datetime.datetime.today().weekday() != 6 and
                (9 <= get_time().hour <= 17)):
            #asyncio.run(get_gold_rate())
            asyncio.run(get_fuel())

    counter = counter + 1

# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    LOGGER = logging.getLogger(__name__)

    LOGGER.info('Display 20x4 LCD Module Start')

    print('Display 20x4 LCD Module Starts')
    display.lcd_display_string("Welcome", 1)
    display.lcd_display_string("Starting Now ...", 2)
    counter = 0
    time.sleep(25)

    try:
        asyncio.run(get_weather())
        asyncio.run(get_gold_rate())
        asyncio.run(get_fuel())
        print_lcd()

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()
