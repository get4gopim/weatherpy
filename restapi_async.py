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
import util

from aiohttp import ClientSession, ClientConnectorError
from collections import namedtuple

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

scheme = 'http'
host = '192.168.29.101'
port = '8080'

weather_url = scheme + '://' + host + ':' + port + '/forecast/weather'
gold_rate_url = scheme + '://' + host + ':' + port + '/forecast/gold'
fuel_rate_url = scheme + '://' + host + ':' + port + '/forecast/fuel'

lcd_disp_length = 20

# get current system time
def get_time():
    return datetime.datetime.now()

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
            update_weather_temp()
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
        LOGGER.exception ('Unable to connect fuel API', ex)
        fuel_info = FuelInfo.FuelInfo(0, 0, "", "")
        fuel_info.set_error(ex)

# update display line strings
def update_weather_temp():
    global line2

    # Make string right justified of length 4 by padding 3 spaces to left
    justl = lcd_disp_length - 4
    temperature = str(weather.get_condition())[0:justl]
    temperature = temperature.ljust(justl, ' ')
    line2 = temperature + ' ' + str(weather.get_temp()) + 'c'

    line2 = line2.ljust(lcd_disp_length, ' ')

# update display line strings
def update_weather_location():
    global line2

    location = weather.get_location()
    delimiter_idx = util.index_of(location, ',')
    if delimiter_idx > 0:
        location = location[0:delimiter_idx]

    # Make string 16 chars only and left justify with space if length is less.
    line2 = location[0:lcd_disp_length]
    line2 = line2.ljust(lcd_disp_length, ' ')

# update display line rate strings
def update_rate_line():
    global line3, line4

    # line4 = 'Gold   ' + rate_info.get_gold22() + ' Silv ' + rate_info.get_silver()
    line3 = 'Gold   Rate     ' + str(rate_info.get_gold22())
    line4 = 'Silver Rate    ' + str(rate_info.get_silver())

    line3 = line3.ljust(lcd_disp_length, ' ')
    line4 = line4.ljust(lcd_disp_length, ' ')

# update display fuel price line
def update_fuel_line():
    global line3, line4

    # line4 = 'Petrol ' + fuel_info.get_petrol() + ' Disel' + fuel_info.get_diesel()
    line3 = 'Petrol Rate    ' + str(fuel_info.get_petrol())
    line4 = 'Diesel Rate    ' + str(fuel_info.get_diesel())

    line3 = line3.ljust(lcd_disp_length, ' ')
    line4 = line4.ljust(lcd_disp_length, ' ')

# display function
def print_lcd():
    global counter
    global rand_bool

    t = threading.Timer(1, print_lcd)
    t.start()

    currentTime = get_time()
    line1 = currentTime.strftime("%d.%m  %a  %H:%M:%S")
    update_weather_temp()
    update_rate_line()

    #print('Writing to display: ', counter)

    change_every_x_secs = 5

    if currentTime.second % change_every_x_secs == 0:
        # print(currentTime.second, ' mod ', currentTime.second % change_every_x_secs, ' display: ', rand_bool)
        if rand_bool:
            update_weather_temp()
            update_rate_line()
            rand_bool = False
        else:
            update_weather_location()
            update_fuel_line()
            rand_bool = True

        if weather.get_error() is None:
            display.lcd_display_string(line2, 2)

    display.lcd_display_string(line1, 1)

    # Every reset counter clear and refresh the data lines
    if counter == 0:
        display.lcd_clear()
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
            asyncio.run(get_gold_rate())
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
    rand_bool = True
    time.sleep(26)

    try:
        asyncio.run(get_weather())
        asyncio.run(get_gold_rate())
        asyncio.run(get_fuel())
        print_lcd()

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()
