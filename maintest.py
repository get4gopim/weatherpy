#!/usr/bin/python
# -*- coding:utf-8 -*-

from epddriver import epd2in13
from queue import Queue

import time
import datetime
from PIL import Image, ImageDraw, ImageFont
from service import HtmlParser2
from utility import util
import sys
import asyncio
import logging
import os
import threading
import schedule
from model import WeatherInfo

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'weatherpy/images')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'weatherpy/fonts')
print(picdir)
print(fontdir)

IMG_LOCATION = picdir
DISPLAY_LENGTH = 20

# Initialize and Clear the display
epd = epd2in13.EPD()
# image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
# draw = ImageDraw.Draw(image)

# font_path = os.path.join(fontdir, 'CarterOne-Regular.ttf')
# print(font_path)
# assert os.path.isfile(font_path)

fontTemperature = ImageFont.truetype(os.path.join(fontdir, 'CarterOne-Regular.ttf'), 20)  # Bold
fontWeekDay = ImageFont.truetype(os.path.join(fontdir, 'CarterOne-Regular.ttf'), 16)
fontTime = ImageFont.truetype(os.path.join(fontdir, 'Bungee-Regular.ttf'), 26)
fontLocation = ImageFont.truetype(os.path.join(fontdir, 'RussoOne-Regular.ttf'), 18)
fontCondition = ImageFont.truetype(os.path.join(fontdir, 'Overlock-Black.ttf'), 18)
fontPreciption = ImageFont.truetype(os.path.join(fontdir, 'Overlock-Black.ttf'), 18)

job_queue = Queue()


def weekday():
    current_time = datetime.datetime.now()
    return current_time.strftime("%A").center(11, ' ')


def day_month():
    current_time = datetime.datetime.now()
    return current_time.strftime("%b %d").center(11, ' ')


def get_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%H:%M')


def call_apis_async(location):
    start = time.time()
    loop = asyncio.get_event_loop()

    f1 = asyncio.Future()

    f1.add_done_callback(callback_weather)

    tasks = []
    if location is not None:
        tasks.append(HtmlParser2.get_google_weather(f1, location))
    else:
        tasks.append(HtmlParser2.get_weather(f1))

    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print()


def call_weather_api(location):
    LOGGER.info("call_weather_api")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        f1 = asyncio.Future()

        f1.add_done_callback(callback_weather)

        tasks = []
        if location is not None:
            tasks.append(HtmlParser2.get_google_weather(f1, location))
        else:
            tasks.append(HtmlParser2.get_weather(f1))

        loop.run_until_complete(asyncio.wait(tasks))

        loop.close()
        print()
    except Exception as ex:
        LOGGER.error(f'call_weather_api : {repr(ex)}')


def callback_weather(future):
    global weather
    weather = future.result()


# update display line strings
def update_weather_high_low():
    line2 = ''

    if weather is not None:
        line2 = weather.get_low() + '~' + weather.get_high() + '°c'

    return line2


# update display line strings
def get_weather_image():
    file_name = 'cloudy.bmp'

    if weather is not None:
        if 'Cloudy' in weather.get_condition():
            file_name = 'clouds.bmp'
        elif 'Shower' in weather.get_condition():
            file_name = 'shower.bmp'
        elif 'Rain' in weather.get_condition():
            file_name = 'rainy.bmp'
        elif 'Fog' in weather.get_condition():
            file_name = 'foggy.bmp'
        elif 'Driz' in weather.get_condition():
            file_name = 'drizzle.bmp'
        elif 'Clear' in weather.get_condition():
            file_name = 'clear_sky.bmp'
        elif 'Haze' in weather.get_condition():
            file_name = 'haze_2.bmp'
        elif 'Thunder' in weather.get_condition():
            file_name = 'thunder_storm.bmp'
        else:
            file_name = 'sun.bmp'

    file_name = os.path.join(IMG_LOCATION, file_name)
    LOGGER.info("Weather Image: " + file_name)
    return file_name


# update display line strings
def update_weather_temp_line2():
    line2 = ''

    if weather is not None:
        # Make string right justified of length 4 by padding 3 spaces to left
        justl = DISPLAY_LENGTH - 4
        temperature = str(weather.get_condition())[0:justl]
        line2 = temperature.ljust(justl, ' ')
        line2 = line2.ljust(DISPLAY_LENGTH, ' ')

    return line2


# update preciption line strings
def update_weather_preciption_line2():
    line2 = ''

    preciption = str(weather.get_preciption())
    if len(preciption) > 0:
        idx = util.index_of(preciption, 'until')
        if idx > 0:
            preciption = preciption[0:idx]

        # Make string 20 chars only and left justify with space if length is less.
        line2 = preciption[0:DISPLAY_LENGTH]
        line2 = line2.ljust(DISPLAY_LENGTH, ' ')
    else:
        update_weather_location_line2()

    return line2


# update preciption line strings
def update_weather_updated():
    line2 = ''

    preciption = str(weather.get_preciption())
    if len(preciption) > 0:
        idx = util.index_of(preciption, 'until')
        if idx > 0:
            preciption = preciption[idx:len(preciption)]

        # Make string 20 chars only and left justify with space if length is less.
        line2 = preciption[0:DISPLAY_LENGTH]
        line2 = line2.ljust(DISPLAY_LENGTH, ' ')
    else:
        update_weather_location_line2()

    return line2


# update display line strings
def update_weather_location_line2():
    line2 = ''

    location = weather.get_location()
    delimiter_idx = util.index_of(location, ',')
    if delimiter_idx > 0:
        location = location[0:delimiter_idx]

    # Make string 16 chars only and left justify with space if length is less.
    line2 = location[0:DISPLAY_LENGTH]
    line2 = line2.ljust(DISPLAY_LENGTH, ' ')

    return line2


def display_elink():
    global image
    global draw

    LOGGER.info("display_elink")
    clear_display()

    # partial update
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
    draw = ImageDraw.Draw(image)

    # outer box
    # draw.rectangle([(0, 0), (epd2in13.EPD_HEIGHT-1, epd2in13.EPD_WIDTH-1)], outline=0)

    # ---------------- Left side content goes here --------------------
    start_y_pos = 40
    draw.text((5, start_y_pos), update_weather_location_line2(), font=fontLocation, fill=0)
    display_weather_info()
    # ---------------- Left side content ends here --------------------

    # ---------------- Right side content goes here --------------------
    # Vertical Middle Line
    draw.line([(160, 5), (160, 118)], fill=0, width=2)

    # Display Weather image & High-Low Temp
    display_weather_img()

    # Horizontal Line with Padding 5
    draw.line([(165, 82), (245, 82)], fill=0, width=2)

    display_date_info()

    epd.display(epd.getbuffer(image))
    time.sleep(2)
    # ---------------- Right side content ends here --------------------

    # Time partial update
    every_sec()

    # epd.sleep()


def clear_display():
    LOGGER.info('Clear Display')
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd.Clear(0xFF)
    time.sleep(5)


def every_sec():
    LOGGER.info ('Time partial update')
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    draw.rectangle((5, 5, 90, 30), fill=255)
    draw.text((5, 5), get_time(), font=fontTime, fill=0)
    crop_image = image.crop([5, 5, 90, 30])
    image.paste(crop_image, (5, 5))
    epd.displayPartial(epd.getbuffer(image))


def display_date_info():
    # global random_bool

    LOGGER.info ('Date partial update')
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    draw.rectangle((165, 85, 250, 122), fill=255)

    draw.text((165, 82), weekday(), font=fontWeekDay, fill=0)
    draw.text((165, 98), day_month(), font=fontWeekDay, fill=0)

    crop_image = image.crop([165, 85, 250, 122])
    image.paste(crop_image, (165, 85))
    epd.displayPartial(epd.getbuffer(image))


def display_weather_info():
    # global random_bool

    LOGGER.info ('Info partial update')
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    draw.rectangle((5, 60, 158, 120), fill=255)

    start_y_pos = 40
    draw.text((5, start_y_pos + 20), update_weather_temp_line2(), font=fontCondition, fill=0)
    draw.text((5, start_y_pos + 40), update_weather_preciption_line2(), font=fontPreciption, fill=0)
    draw.text((5, start_y_pos + 60), update_weather_updated(), font=fontPreciption, fill=0)

    crop_image = image.crop([5, 60, 158, 120])
    image.paste(crop_image, (5, 60))
    epd.displayPartial(epd.getbuffer(image))


def display_weather_img():
    # global random_bool

    LOGGER.info ('Image partial update')
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    epd.Clear(0xFF)
    time.sleep(2)

    draw.rectangle((162, 2, 250, 80), fill=255)

    # Weather High Low
    draw.text((165, 55), update_weather_high_low(), font=fontTemperature, fill=0)

    # weather bmp file size: 52x44 | 64x42
    weather_img = Image.open(get_weather_image())
    image.paste(weather_img, (180, 2))

    crop_image = image.crop([162, 2, 250, 80])
    image.paste(crop_image, (162, 2))
    epd.displayPartial(epd.getbuffer(image))


def worker_main():
    while 1:
        try:
            job_func, job_args = job_queue.get()
            job_func(*job_args)
            job_queue.task_done()
        except BaseException as ex:
            LOGGER.error(f'worker_main : {repr(ex)}')


def run_weather_thread(job_vars):
    job_func, job_args = job_vars
    job_thread = threading.Thread(target=job_func, args=job_args)
    job_thread.start()


def add_scheduler(location):
    # Update time every minutes
    schedule.every(30).seconds.do(job_queue.put, (every_sec, []))

    # Update weather every 13 mins once
    schedule.every(13).minutes.do(run_weather_thread, (call_weather_api, [location]))

    # Update weather every 15 mins once
    schedule.every(15).minutes.do(job_queue.put, (display_weather_img, []))

    # Update weather every 17 mins once
    schedule.every(17).minutes.do(job_queue.put, (display_weather_info, []))

    # Update day info every day starts
    schedule.every().days.at('00:00').do(job_queue.put, (display_date_info, []))

# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    location = None
    if len(sys.argv) > 1:
        location = sys.argv[1]

    random_bool = False

    try:
        LOGGER.info("Initializing Display")
        # clear_display()

        worker_thread = threading.Thread(target=worker_main)
        worker_thread.start()

        call_apis_async(location)

        add_scheduler(location)

        display_elink()

        while 1:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        exit()

