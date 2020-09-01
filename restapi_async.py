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
import HtmlParser
import util

from aiohttp import ClientSession, ClientConnectorError
from collections import namedtuple

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()


lcd_disp_length = 20
service_start_time_in_secs = 2


# get current system time
def get_time():
    return datetime.datetime.now()


# call async rest call to get weather details
async def get_weather():
    global weather
    try:
        weather = HtmlParser.get_weather()
        weather.set_error(None)
        update_weather_temp()
        return weather
    except Exception as ex:
        LOGGER.error('Unable to connect weather API ' + getattr(ex, 'message', repr(ex)))
        weather = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "", "")
        weather.set_error(ex)


# call async rest call to get gold rate detail
async def get_gold_rate():
    global rate_info
    try:
        rate_info = HtmlParser.get_gold_price()
        rate_info.set_error(None)
        update_rate_line()
        return rate_info
    except Exception as ex:
        LOGGER.error('Unable to connect rate API ' + getattr(ex, 'message', repr(ex)))
        rate_info = RateInfo.RateInfo('0', '0', 0.0, "", "")
        rate_info.set_error(ex)


# call async rest call to get fuel details
async def get_fuel():
    global fuel_info
    try:
        fuel_info = HtmlParser.get_fuel_price()
        fuel_info.set_error(None)
        update_fuel_line()
        return fuel_info
    except Exception as ex:
        LOGGER.error('Unable to connect Fuel API ' + getattr(ex, 'message', repr(ex)))
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

# update preciption line strings
def update_weather_preciption():
    global line2

    preciption = str(weather.get_preciption())
    if len(preciption) > 0:
        idx = util.index_of(preciption, 'until')
        if idx > 0:
            preciption = preciption[0:idx]

        # Make string 20 chars only and left justify with space if length is less.
        line2 = preciption[0:lcd_disp_length]
        line2 = line2.ljust(lcd_disp_length, ' ')
    else:
        update_weather_location()
        

# update display line rate strings
def update_rate_line():
    global line3, line4

    just = lcd_disp_length - 5
    prefix_p = 'Gold'
    prefix_d = 'Silver'

    line3 = prefix_p.ljust(just, ' ') + ' ' + str(rate_info.get_gold22())
    line4 = prefix_d.ljust(just, ' ') + str(rate_info.get_silver())


# update display fuel price line
def update_fuel_line():
    global line5, line6

    just = lcd_disp_length - 6
    prefix_p = 'Petrol'
    prefix_d = 'Diesel'

    line5 = prefix_p.ljust(just, ' ') + str(fuel_info.get_petrol())
    line6 = prefix_d.ljust(just, ' ') + str(fuel_info.get_diesel())

    # line4 = 'Petrol ' + fuel_info.get_petrol() + ' Disel' + fuel_info.get_diesel()
    # line5 = 'Petrol        ' + str(fuel_info.get_petrol())
    # line6 = 'Diesel        ' + str(fuel_info.get_diesel())

    # line5 = line5.ljust(lcd_disp_length, ' ')
    # line6 = line6.ljust(lcd_disp_length, ' ')


def update_time_line(currentTime):
    global line1

    line1 = currentTime.strftime("%d.%m  %a  %H:%M:%S")


def print_line1():
    display.lcd_display_string(line1, 1)


def print_line2():
    if weather.get_error() is None:
        display.lcd_display_string(line2, 2)


# print line 3 and 4
def print_line3_and_4_rate():
    if rate_info.get_error() is None:
        display.lcd_display_string(line3, 3)
        display.lcd_display_string(line4, 4)


# print line 3 and 4
def print_line3_and_4_fuel():
    if fuel_info.get_error() is None:
        display.lcd_display_string(line5, 3)
        display.lcd_display_string(line6, 4)


# display function
def print_lcd():
    global line1
    global counter
    global rand_bool

    t = threading.Timer(1, print_lcd)
    t.start()

    currentTime = get_time()
    update_time_line(currentTime)

    # Every reset counter clear and refresh the data lines
    if counter == 0:
        LOGGER.info('need to clear display ?')
        display.lcd_clear()


    print_line1()
    change_every_x_secs = 5

    # change display line2 every x seconds
    if currentTime.second % change_every_x_secs == 0:
        # print(currentTime.second, ' mod ', currentTime.second % change_every_x_secs, ' display: ', rand_bool)
        print_line2()

        if rand_bool:
            update_weather_temp()
            rand_bool = False
        else:
            update_weather_preciption()
            rand_bool = True

    if 0 <= currentTime.second <= 30:
        update_rate_line()
        print_line3_and_4_rate()
    else:
        update_fuel_line()
        print_line3_and_4_fuel()

    # Refresh the data every 5 mins (300 seconds once)
    if counter == 30:
        counter = 0
        asyncio.run(get_weather())
        # Query Gold Rate only in between 9 AM to 6 PM and not on SUNDAYS
        if (currentTime.weekday() != 6 and
                (9 <= currentTime.hour <= 17)):
            asyncio.run(get_gold_rate())

        # Query Fuel Rate only in morning between 6 AM to 8 AM and not on SUNDAYS
        if (currentTime.weekday() != 6 and
                    (6 <= currentTime.hour <= 7)):
            asyncio.run(get_fuel())
    else:
        counter = counter + 1


def welcome_date_month():
    current_time = get_time()
    day = current_time.strftime("%d")
    month = current_time.strftime("%B")
    week_day = current_time.strftime("%A")

    if current_time.month == 9 and current_time.weekday() in [2, 3, 5]:
        month = current_time.strftime("%b")

    # Format: 29 August Sunday, 22 Sep Wednesday
    wel_date = str (day + ' ' + month + ' ' + week_day)
    return wel_date.center(lcd_disp_length, ' ')


# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    LOGGER = logging.getLogger(__name__)

    LOGGER.info('Display 20x4 LCD Module Start')

    print('Display 20x4 LCD Module Starts')
    display.lcd_display_string("Welcome".center(lcd_disp_length, ' '), 1)
    display.lcd_display_string(welcome_date_month(), 2)
    display.lcd_display_string("Starting Now ...".center(lcd_disp_length, ' '), 4)

    counter = 0
    rand_bool = True
    time.sleep(service_start_time_in_secs)

    try:
        asyncio.run(get_weather())
        asyncio.run(get_gold_rate())
        asyncio.run(get_fuel())
        print_lcd()

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()
