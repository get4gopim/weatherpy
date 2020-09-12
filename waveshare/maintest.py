#!/usr/bin/python
# -*- coding:utf-8 -*-

from waveshare import epd2in13
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
from service import HtmlParser2
from utility import util
from model import WeatherInfo
import traceback
import sys
import threading
import asyncio
import logging
import os
import schedule


IMG_LOCATION = '../images/'
DISPLAY_LENGTH = 20
# Initialize and Clear the display
epd = epd2in13.EPD()


def weekday():
    current_time = datetime.datetime.now()
    return current_time.strftime("%A")


def day_month():
    current_time = datetime.datetime.now()
    return current_time.strftime("%b %d")


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



def callback_weather(future):
    global weather
    weather = future.result()

# update display line strings
def update_weather_high_low():
    line2 = ''

    if weather is not None:
        line2 = weather.get_low() + '~' + weather.get_high() + "°c"

    return line2

# update display line strings
def get_weather_image():
    file_name = 'cloudy.bmp'

    if weather is not None:
        if 'Cloudy' in weather.get_condition():
            file_name = 'cloudy.bmp'
        elif 'Rain' in weather.get_condition():
            file_name = 'rainy.bmp'
        elif 'Fog' in weather.get_condition():
            file_name = 'foggy.bmp'
        elif 'Driz' in weather.get_condition():
            file_name = 'drizzle.bmp'
        elif 'Clear' in weather.get_condition():
            file_name = 'clear_sky.bmp'
        elif 'Haze' in weather.get_condition():
            file_name = 'haze.bmp'
        elif 'Thunder' in weather.get_condition():
            file_name = 'thunder_storm.bmp'
        else:
            file_name = 'cloudy.bmp'

    file_name = IMG_LOCATION + file_name
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


fontTemperature = ImageFont.truetype('/usr/share/fonts/truetype/google/CarterOne-Regular.ttf', 20)  # Bold
fontWeekDay = ImageFont.truetype('/home/pi/fonts/Roboto-Black.ttf', 16)
fontTime = ImageFont.truetype('/home/pi/fonts/Roboto-Black.ttf', 24)
fontLocation = ImageFont.truetype('/home/pi/fonts/Roboto-Medium.ttf', 18)


def display_elink():
    # partial update
    epd.init(epd.PART_UPDATE)
    epd.Clear(0xFF)
    font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 20)
    image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
    draw = ImageDraw.Draw(image)

    # outer box
    # draw.rectangle([(0, 0), (epd2in13.EPD_HEIGHT-1, epd2in13.EPD_WIDTH-1)], outline=0)

    # ---------------- Left side content goes here --------------------
    start_y_pos = 40
    draw.text((5, start_y_pos), update_weather_location_line2(), font=fontLocation, fill=0)
    draw.text((5, start_y_pos+20), update_weather_temp_line2(), font=fontLocation, fill=0)
    draw.text((5, start_y_pos+40), update_weather_preciption_line2(), font=fontLocation, fill=0)
    draw.text((5, start_y_pos+60), update_weather_updated(), font=fontLocation, fill=0)
    # ---------------- Left side content ends here --------------------

    # ---------------- Right side content goes here --------------------
    # Vertical Middle Line
    draw.line([(160, 5), (160, 118)], fill=0, width=0)

    # weather bmp file size: 52x44 | 64x42
    weather_img = Image.open(get_weather_image())
    image.paste(weather_img, (180, 5))

    # Horizontal Line with Padding 5
    draw.line([(165, 80), (245, 80)], fill=0, width=0)

    draw.text((165, 50), update_weather_high_low(), font=fontTemperature, fill=0)
    draw.text((170, 80), weekday(), font=fontWeekDay, fill=0)
    draw.text((180, 100), day_month(), font=fontWeekDay, fill=0)


    # read bmp file
    weather_img = Image.open(get_weather_image())
    image.paste(weather_img, (180, 5))
    epd.display(epd.getbuffer(image))
    time.sleep(2)
    # ---------------- Right side content ends here --------------------

    while (True):
        draw.rectangle((5, 5, 80, 30), fill=255)
        draw.text((5, 5), get_time(), font=fontTime, fill=0)
        crop_image = image.crop([5, 5, 80, 30])
        image.paste(crop_image, (5, 5))
        epd.displayPartial(epd.getbuffer(image))
        time.sleep(60)

    # epd.sleep()

# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    location = None
    if len(sys.argv) > 1:
        location = sys.argv[1]

    try:
        LOGGER.info("Initializing Display")
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        epd.Clear(0xFF)

        call_apis_async(location)

        display_elink()

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        exit()

