# Main LCD 16x2 I2C - Forecast API Consume Python Script
import random
import threading
import asyncio
import json
import logging
import os
import sched

import datetime
import time

import lcddriver

import WeatherInfo
import RateInfo
import FuelInfo
import HtmlParser
import HtmlParser2
import util

from aiohttp import ClientSession, ClientConnectorError
from collections import namedtuple

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()


lcd_disp_length = 20
service_start_time_in_secs = 1

refresh_weather_in_x_secs = 60
s = sched.scheduler(time.time, time.sleep)

# get current system time
def get_time():
    return datetime.datetime.now()

def initalize_default():
    print ('init default')
    weather = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "", "", "")
    rate_info = RateInfo.RateInfo('0', '0', 0.0, "", "")
    fuel_info = FuelInfo.FuelInfo(0, 0, "", "")


def call_apis_async():
    # global weather, rate_info, fuel_info
    # initalize_default()

    start = time.time()
    loop = asyncio.get_event_loop()

    f1 = asyncio.Future()
    f2 = asyncio.Future()
    f3 = asyncio.Future()

    f1.add_done_callback( callback_weather)
    f2.add_done_callback(callback_gold)
    f3.add_done_callback(callback_fuel)

    tasks = [HtmlParser2.get_weather(f1), HtmlParser2.get_gold_price(f2), HtmlParser2.get_fuel_price(f3)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print()


def call_weather_api():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_weather)

    LOGGER.debug ("before weather")
    tasks = [HtmlParser2.get_weather(f1)]
    loop.run_until_complete(asyncio.wait(tasks))
    LOGGER.debug ("completed")

    # time.sleep(5)

    loop.close()
    print()


def call_gold_api():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_gold)

    tasks = [HtmlParser2.get_gold_price(f1)]
    loop.run_until_complete(asyncio.wait(tasks))

    # time.sleep(5)

    loop.close()
    print()


def call_fuel_api():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_fuel)

    tasks = [HtmlParser2.get_fuel_price(f1)]
    loop.run_until_complete(asyncio.wait(tasks))

    # time.sleep(5)

    loop.close()
    print()

def callback_weather(future):
    global weather
    weather = future.result()


def callback_gold(future):
    global rate_info
    rate_info = future.result()


def callback_fuel(future):
    global fuel_info
    fuel_info = future.result()


# call async rest call to get weather details
# async def get_weather():
#     global weather
#     try:
#         weather = HtmlParser.get_weather()
#         weather.set_error(None)
#         update_weather_temp()
#         return weather
#     except Exception as ex:
#         LOGGER.error('Unable to connect weather API ' + getattr(ex, 'message', repr(ex)))
#         weather = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "", "")
#         weather.set_error(ex)


# call async rest call to get gold rate detail
# async def get_gold_rate():
#     global rate_info
#     try:
#         rate_info = HtmlParser.get_gold_price()
#         rate_info.set_error(None)
#         update_rate_line()
#         return rate_info
#     except Exception as ex:
#         LOGGER.error('Unable to connect rate API ' + getattr(ex, 'message', repr(ex)))
#         rate_info = RateInfo.RateInfo('0', '0', 0.0, "", "")
#         rate_info.set_error(ex)


# call async rest call to get fuel details
# async def get_fuel():
#     global fuel_info
#     try:
#         fuel_info = HtmlParser.get_fuel_price()
#         fuel_info.set_error(None)
#         update_fuel_line()
#         return fuel_info
#     except Exception as ex:
#         LOGGER.error('Unable to connect Fuel API ' + getattr(ex, 'message', repr(ex)))
#         fuel_info = FuelInfo.FuelInfo(0, 0, "", "")
#         fuel_info.set_error(ex)


# update display line strings
def update_weather_temp():
    global line2

    if weather is not None:
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


def refresh_weather_data():
    tick = 0
    refresh_interval = 60

    LOGGER.info ('refresh_weather_data')
    t = threading.Timer(refresh_interval, refresh_weather_data)
    t.start()

    call_weather_api()


# display function
def print_lcd():
    global line1
    global rand_bool
    global counter

    t = threading.Timer(1, print_lcd)
    t.start()

    # Every reset counter clear and refresh the data lines
    if counter == 0:
        LOGGER.info (f'clear lcd called counter: {counter}')
        display.lcd_clear()
        # update_weather_temp()

    currentTime = get_time()
    update_time_line(currentTime)

    # LOGGER.info (f'counter = {counter} currentTime = {currentTime}')

    print_line1()
    # change_every_x_secs = 10
    #
    # # change display line2 every x seconds
    # if currentTime.second % change_every_x_secs == 0:
    #     # print(currentTime.second, ' mod ', currentTime.second % change_every_x_secs, ' display: ', rand_bool)
    #     if rand_bool:
    #         update_weather_temp()
    #         rand_bool = False
    #     else:
    #         update_weather_preciption()
    #         rand_bool = True
    #     print_line2()

    if 0 <= currentTime.second <= 30:
        update_weather_temp()
        update_rate_line()
        print_line2()
        print_line3_and_4_rate()
    else:
        update_weather_preciption()
        update_fuel_line()
        print_line2()
        print_line3_and_4_fuel()

    # Refresh the data every 5 mins (300 seconds once)
    if counter == 60:
        counter = 0
        # call_weather_api()

        # # Query Gold Rate only in between 9 AM to 6 PM and not on SUNDAYS
        # if (currentTime.weekday() != 6 and
        #         (9 <= currentTime.hour <= 16)):
        #     call_gold_api()
        #
        # # Query Fuel Rate only in morning between 6 AM to 8 AM and not on SUNDAYS
        # if (currentTime.weekday() != 6 and
        #             (6 <= currentTime.hour <= 7)):
        #     call_fuel_api()
        #
        # LOGGER.info (f'returned {currentTime} counter: {counter}')
    else:
        counter = counter + 1


def refresh_weather_data (sc):
    LOGGER.info ("Doing stuff...")
    # do your stuff
    call_weather_api()

    s.enter(refresh_weather_in_x_secs, 1, refresh_weather_data, (sc,))


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

    # print('Display 20x4 LCD Module Starts')
    display.lcd_display_string("Welcome".center(lcd_disp_length, ' '), 1)
    display.lcd_display_string(welcome_date_month(), 2)
    display.lcd_display_string("Starting Now ...".center(lcd_disp_length, ' '), 4)

    counter = 0
    rand_bool = True
    time.sleep(service_start_time_in_secs)

    try:
        call_apis_async()
        print_lcd()

        s.enter(refresh_weather_in_x_secs, 1, refresh_weather_data, (s,))
        s.run()

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()
