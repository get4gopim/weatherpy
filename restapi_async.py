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
service_start_time_in_secs = 3


# get current system time
def get_time():
    return datetime.datetime.now()


# call async rest call to get weather details
async def get_weather():
    global weather
    try:
        weather = HtmlParser.get_weather()
        weather.set_error(None)
        update_weather_location()
        return weather
    except Exception as ex:
        print('Unable to connect weather API')
        weather = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "")
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
        print('Unable to connect rate API')
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
        LOGGER.exception('Unable to connect Fuel API', ex)
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

    preciption = weather.get_preciption()
    delimiter_idx = util.index_of(preciption, ' until')
    if delimiter_idx > 0:
        preciption = preciption[0:delimiter_idx]

    # Make string 16 chars only and left justify with space if length is less.
    line2 = preciption[0:lcd_disp_length]
    line2 = line2.rjust(lcd_disp_length, ' ')

# update display line rate strings
def update_rate_line():
    global line3, line4

    # line4 = 'Gold   ' + rate_info.get_gold22() + ' Silv ' + rate_info.get_silver()
    line3 = 'Gold            ' + str(rate_info.get_gold22())
    line4 = 'Silver         ' + str(rate_info.get_silver())

    line3 = line3.ljust(lcd_disp_length, ' ')
    line4 = line4.ljust(lcd_disp_length, ' ')


# update display fuel price line
def update_fuel_line():
    global line3, line4

    # line4 = 'Petrol ' + fuel_info.get_petrol() + ' Disel' + fuel_info.get_diesel()
    line3 = 'Petrol         ' + str(fuel_info.get_petrol())
    line4 = 'Diesel         ' + str(fuel_info.get_diesel())

    line3 = line3.ljust(lcd_disp_length, ' ')
    line4 = line4.ljust(lcd_disp_length, ' ')


def update_time_line(currentTime):
    global line1

    line1 = currentTime.strftime("%d.%m  %a  %H:%M:%S")


def print_line1():
    display.lcd_display_string(line1, 1)


def print_line2():
    if weather.get_error() is None:
        display.lcd_display_string(line2, 2)


# print line 3 and 4
def print_line3_and_4():
    if rate_info.get_error() is None and fuel_info.get_error() is None:
        display.lcd_display_string(line3, 3)
        display.lcd_display_string(line4, 4)


# display function
def print_lcd():
    global line1
    global counter
    global rand_bool

    t = threading.Timer(1, print_lcd)
    t.start()

    currentTime = get_time()
    update_time_line(currentTime)
    # print timer every in second
    print_line1()

    update_weather_temp()
    update_rate_line()

    #print('Writing to display: ', counter)

    change_every_x_secs = 10

    # change display line2 every x seconds
    if currentTime.second % change_every_x_secs == 0:
        # print(currentTime.second, ' mod ', currentTime.second % change_every_x_secs, ' display: ', rand_bool)
        if rand_bool:
            update_weather_temp()
            update_rate_line()
            rand_bool = False
        else:
            update_weather_preciption()
            update_fuel_line()
            rand_bool = True
        print_line2()
        print_line3_and_4()



    # Every reset counter clear and refresh the data lines
    if counter == 0:
        display.lcd_clear()
        print_line1()
        print_line3_and_4()

    # Refresh the data every 5 mins (300 seconds once)
    if counter == 300:
        counter = 0
        asyncio.run(get_weather())
        # Query Gold Rate only in between 9 AM to 5 PM and not on SUNDAYS
        if (datetime.datetime.today().weekday() != 6 and
                (9 <= get_time().hour <= 17)):
            asyncio.run(get_gold_rate())

        # Query Fuel Rate only in morning between 6 AM to 8 AM and not on SUNDAYS
        if (datetime.datetime.today().weekday() != 6 and
                    (6 <= get_time().hour <= 8)):
            asyncio.run(get_fuel())

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
