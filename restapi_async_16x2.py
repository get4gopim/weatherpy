# Main LCD 20x4 I2C - Forecast API Python Script

import threading
import asyncio
import logging
import os
import schedule
import datetime
import time

from lcddriver import lcddriver_16x2

from parser import HtmlParser2
from utility import util

from queue import Queue

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver_16x2.lcd()

lcd_disp_length = 16
service_start_time_in_secs = 10

jobqueue = Queue()


# get current system time
def get_time():
    return datetime.datetime.now()


def call_apis_async():
    start = time.time()
    loop = asyncio.get_event_loop()

    f1 = asyncio.Future()
    f2 = asyncio.Future()
    # f3 = asyncio.Future()

    f1.add_done_callback(callback_weather)
    f2.add_done_callback(callback_gold)
    # f3.add_done_callback(callback_fuel)

    tasks = [HtmlParser2.get_weather(f1), HtmlParser2.get_gold_price(f2)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print()


def call_weather_api():
    LOGGER.info("call_weather_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_weather)

    tasks = [HtmlParser2.get_weather(f1)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()
    print()


def call_gold_api():
    LOGGER.info("call_gold_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_gold)

    tasks = [HtmlParser2.get_gold_price(f1)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()
    print()


def call_fuel_api():
    LOGGER.info("call_fuel_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback_fuel)

    tasks = [HtmlParser2.get_fuel_price(f1)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()
    print()


def callback_weather(future):
    global weather
    weather = future.result()
    # update_weather_temp()
    update_weather_preciption_line2()


def callback_gold(future):
    global rate_info
    rate_info = future.result()
    update_rate_line_3_4()


def callback_fuel(future):
    global fuel_info
    fuel_info = future.result()
    update_fuel_line_3_4()


# update display line strings
def update_weather_temp_line2():
    global line2

    if weather is not None:
        # Make string right justified of length 4 by padding 3 spaces to left
        justl = lcd_disp_length - 4
        temperature = str(weather.get_condition())[0:justl]
        temperature = temperature.ljust(justl, ' ')
        line2 = temperature + ' ' + str(weather.get_temp()) + 'c'

        line2 = line2.ljust(lcd_disp_length, ' ')


# update display line strings
def update_weather_location_line2():
    global line2

    location = weather.get_location()
    delimiter_idx = util.index_of(location, ',')
    if delimiter_idx > 0:
        location = location[0:delimiter_idx]

    # Make string 16 chars only and left justify with space if length is less.
    line2 = location[0:lcd_disp_length]
    line2 = line2.ljust(lcd_disp_length, ' ')


# update preciption line strings
def update_weather_preciption_line2():
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
        update_weather_location_line2()


# update display line rate strings
def update_rate_line_3_4():
    global line2

    just = lcd_disp_length - 5
    prefix_p = 'G'
    prefix_d = 'S'

    # line3 = prefix_p.ljust(just, ' ') + ' ' + str(rate_info.get_gold22())
    line2 = prefix_p + ' ' + str(rate_info.get_gold22()) + ' | ' + prefix_d + ' ' +  str(rate_info.get_silver())
    line2 = line2.ljust(lcd_disp_length, ' ')


# update display fuel price line
def update_fuel_line_3_4():
    global line5
    global line6

    just = lcd_disp_length - 5
    prefix_p = 'P'
    prefix_d = 'D'

    line2 = prefix_p + ' ' + str(rate_info.get_gold22()) + ' | ' + str(rate_info.get_silver())


def update_time_line1(currentTime):
    global line1

    line1 = currentTime.strftime("%d.%b  %H:%M:%S")


def print_line1():
    display.lcd_display_string(line1, 1)


def print_line2():
    if weather.get_error() is None:
        display.lcd_display_string(line2, 2)


def every_second():
    global counter
    global rand_bool
    global _bool_20

    current_time = get_time()
    update_time_line1(current_time)
    print_line1()

    if counter == 0:
        print_line2()
        counter = counter + 1
        return

    change_every_x_secs = 20
    if counter % change_every_x_secs == 0:
        if _bool_20:
            update_weather_temp_line2()
            _bool_20 = False
        else:
            update_weather_preciption_line2()
            _bool_20 = True
        print_line2()
        counter = counter + 1
        return

    change_every_x_secs = 10
    # change display line2 every x seconds
    if counter % change_every_x_secs == 0:
        if rand_bool:
            update_weather_location_line2()
            rand_bool = False
        else:
            # update_weather_preciption_line2()
            update_rate_line_3_4()
            rand_bool = True
        print_line2()

    counter = counter + 1

    # Refresh the data every 5 mins (300 seconds once)
    # if counter == 300:
    #     counter = 0


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()


def welcome_date_month():
    current_time = get_time()
    day = current_time.strftime("%d")
    month = current_time.strftime("%b")
    week_day = current_time.strftime("%A")

    if current_time.month == 9 and current_time.weekday() in [2, 3, 5]:
        month = current_time.strftime("%b")

    # Format: 29 August Sunday, 22 Sep Wednesday
    wel_date = str(day + ' ' + month + ' ' + week_day)
    return wel_date.center(lcd_disp_length, ' ')


def add_scheduler():
    # Update time every second
    schedule.every(1).seconds.do(jobqueue.put, every_second)

    # Update weather every 15 mins once every day
    schedule.every(15).minutes.do(jobqueue.put, call_weather_api)

    # Update gold rate every 1 hour except sunday from 10 AM to 5 PM
    gold_times = ["10:00", "11:00", "12:00", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "17:00"]
    for x in gold_times:
        schedule.every().monday.at(x).do(call_gold_api)
        schedule.every().tuesday.at(x).do(call_gold_api)
        schedule.every().wednesday.at(x).do(call_gold_api)
        schedule.every().thursday.at(x).do(call_gold_api)
        schedule.every().friday.at(x).do(call_gold_api)
        schedule.every().saturday.at(x).do(call_gold_api)

    # Update fuel rate from 6 to 8 AM except sunday
    fuel_times = ["06:00", "06:30", "07:00", "07:30", "08:00"]
    for x in fuel_times:
        schedule.every().monday.at(x).do(call_fuel_api)
        schedule.every().tuesday.at(x).do(call_fuel_api)
        schedule.every().wednesday.at(x).do(call_fuel_api)
        schedule.every().thursday.at(x).do(call_fuel_api)
        schedule.every().friday.at(x).do(call_fuel_api)
        schedule.every().saturday.at(x).do(call_fuel_api)


# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    LOGGER.info('Display 20x4 LCD Module Start')

    display.lcd_display_string("Welcome".center(lcd_disp_length, ' '), 1)
    display.lcd_display_string(welcome_date_month(), 2)
    display.lcd_display_string("Starting Now ...".center(lcd_disp_length, ' '), 4)

    counter = 0
    rand_bool = True
    _bool_20 = True
    time.sleep(service_start_time_in_secs)

    try:
        worker_thread = threading.Thread(target=worker_main)
        worker_thread.start()

        call_apis_async()

        update_weather_temp_line2()
        update_rate_line_3_4()
        # update_fuel_line_3_4()

        add_scheduler()

        display.lcd_clear()
        while 1:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()