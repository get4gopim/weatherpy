#!/usr/bin/python
# -*- coding:utf-8 -*-

from epddriver2in9 import epd2in9
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
DEFAULT_LOC_UUID = '4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d'

# Initialize and Clear the display
epd = epd2in9.EPD()
# image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
# draw = ImageDraw.Draw(image)

# font_path = os.path.join(fontdir, 'CarterOne-Regular.ttf')
# print(font_path)
# assert os.path.isfile(font_path)

fontTemperature = ImageFont.truetype(os.path.join(fontdir, 'CarterOne-Regular.ttf'), 20)  # Bold
fontWeekDay = ImageFont.truetype(os.path.join(fontdir, 'CarterOne-Regular.ttf'), 16)
# fontTime = ImageFont.truetype(os.path.join(fontdir, 'Bungee-Regular.ttf'), 20)
fontTime = ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 26)
fontLocation = ImageFont.truetype(os.path.join(fontdir, 'RussoOne-Regular.ttf'), 18)
fontCondition = ImageFont.truetype(os.path.join(fontdir, 'Overlock-Black.ttf'), 16)
fontPreciption = ImageFont.truetype(os.path.join(fontdir, 'Overlock-Black.ttf'), 18)

font8 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Light.ttf'), 12)
font14 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Light.ttf'), 14)
font12 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Light.ttf'), 12)
fontHiLow= ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 20)
fontTemp = ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 26)
fontTemp18 = ImageFont.truetype(os.path.join(fontdir, 'ThunderDemo.ttf'), 36)

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
    f2 = asyncio.Future()

    f1.add_done_callback(callback_weather)
    f2.add_done_callback(callback_weather_forecast)

    tasks = []
    if util.is_uuid(location):
        tasks.append(HtmlParser2.get_weather(f1, location))
        tasks.append(HtmlParser2.get_weather_forecast(f2, location))
    else:
        tasks.append(HtmlParser2.get_google_weather(f1, location))
        tasks.append(HtmlParser2.get_google_forecast(f2, location))

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
        if util.is_uuid(location):
            tasks.append(HtmlParser2.get_weather(f1, location))
        else:
            tasks.append(HtmlParser2.get_google_weather(f1, location))

        loop.run_until_complete(asyncio.wait(tasks))

        loop.close()
        print()
    except Exception as ex:
        LOGGER.error(f'call_weather_api : {repr(ex)}')


def callback_weather_init(future):
    global weather
    weather = WeatherInfo.WeatherInfo('32', "18", "22", "00:00", "Foggy", "Thalambur", "75%")
    weather.set_humidity("95%")


def callback_weather(future):
    global weather
    weather = future.result()


def callback_weather_forecast(future):
    global forecast
    forecast = future.result()


def call_weather_forecast(location):
    LOGGER.info("call_weather_forecast")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        f1 = asyncio.Future()

        f1.add_done_callback(callback_weather_forecast)

        tasks = []
        if util.is_uuid(location):
            tasks.append(HtmlParser2.get_weather_forecast(f1, location))
        else:
            tasks.append(HtmlParser2.get_google_forecast(f1, location))

        loop.run_until_complete(asyncio.wait(tasks))

        loop.close()
        print()
    except Exception as ex:
        LOGGER.error(f'call_weather_forecast : {repr(ex)}')


# update display line strings
def update_weather_high_low():
    line2 = ''

    if weather is not None:
        line2 = weather.get_low() + '~' + weather.get_high() + '°c'

    return line2


# update display line strings
def get_weather_image(condition):
    file_name = 'cloudy.bmp'

    condition = condition.lower()

    if condition is not None:
        if 'cloudy' in condition:
            file_name = 'mostlycloudy.bmp'
        elif 'shower' in condition:
            file_name = 'shower.bmp'
        elif 'rain' in condition:
            file_name = 'rainy.bmp'
        elif 'fog' in condition:
            file_name = 'foggy.bmp'
        elif 'driz' in condition:
            file_name = 'drizzle.bmp'
        elif 'clear' in condition:
            file_name = 'clear_sky.bmp'
        elif 'haze' in condition:
            file_name = 'haze_2.bmp'
        elif 'thunder' in condition:
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
def get_preciption():
    line2 = ''
    if weather is not None:
        preciption = str(weather.get_preciption())
        idx = util.index_of(preciption, '%')
        if idx > 0:
            preciption = preciption[0:idx+1]

        line2 = preciption

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

    # LOGGER.info("display_elink")
    clear_display()

    # partial update
    epd.init(epd.lut_partial_update)
    epd.Clear(0xFF)
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    # outer box
    # draw.rectangle([(0, 0), (epd2in13.EPD_HEIGHT-1, epd2in13.EPD_WIDTH-1)], outline=0)

    # Vertical Middle Line
    draw.line([(120, 5), (120, epd.width - 5)], fill=0, width=1)

    # Time Horizontal Line
    draw.line([(125, 30), (epd.height - 5, 30)], fill=0, width=1)

    # Vertical Forecast Line
    # draw.line([(210, 35), (210, epd.width - 5)], fill=0, width=1)

    # ---------------- Left side content goes here --------------------
    start_y_pos = 40
    # draw.text((5, start_y_pos), update_weather_location_line2(), font=fontLocation, fill=0)
    # display_weather_info()
    # ---------------- Left side content ends here --------------------

    # ---------------- Right side content goes here --------------------

    epd.display(epd.getbuffer(image))
    time.sleep(2)
    # ---------------- Right side content ends here --------------------

    # Time partial update
    every_sec()
    display_date_info()
    display_weather_main()
    display_weather_forecast()


def clear_display():
    LOGGER.info('Clear Display')
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    # epd.Clear(0xFF)
    time.sleep(2)


def every_sec():
    # LOGGER.info ('Time partial update')
    # epd.init(epd.lut_partial_update)
    # epd.Clear(0xFF)
    x = 245
    draw.rectangle((x, 5, epd.height, 28), fill=255)
    draw.text((x, 5), time.strftime('%H:%M'), font=fontTime, fill=0)
    crop_image = image.crop([x, 5, epd.height, 28])
    image.paste(crop_image, (x, 5))
    epd.display(epd.getbuffer(image))


def display_date_info():
    # global random_bool
    LOGGER.info ('Date partial update')
    # epd.init(epd.lut_partial_update)
    # epd.Clear(0xFF)
    draw.rectangle((125, 5, 240, 28), fill=255)
    draw.text((125, 0), time.strftime("%b %d, %A "), font=font12, fill=0)
    draw.text((125, 13), time.strftime(update_weather_location_line2()), font=font12, fill=0)
    crop_image = image.crop([125, 5, 240, 28])
    image.paste(crop_image, (125, 5))
    epd.display(epd.getbuffer(image))


def display_weather_main():
    # global random_bool

    LOGGER.info ('Info partial update')
    # epd.init(epd.lut_partial_update)
    # epd.Clear(0xFF)

    draw.rectangle((0, 0, 118, epd.width), fill=255)

    if weather is not None:
        bmp = Image.open(get_weather_image(weather.get_condition()))
        image.paste(bmp, (30, 5))

        draw.text((5, 20), 'Hi', font=font14, fill=0)
        draw.text((5, 40), weather.get_high(), font=fontHiLow, fill=0)

        # bmp = Image.open(os.path.join(picdir, 'thermo_sun.bmp'))
        # image.paste(bmp, (30, 60))
        draw.text((40, 60), weather.get_temp(), font=fontTemp, fill=0)
        draw.text((65, 60), '°c', font=font8, fill=0)

        draw.text((97, 20), 'Lo', font=font14, fill=0)
        draw.text((97, 40), weather.get_low(), font=fontHiLow, fill=0)

        draw.text((5, 82), weather.get_condition() + ' ', font=font14, fill=0)

        bmp = Image.open(os.path.join(picdir, 'humidity.bmp'))
        image.paste(bmp, (5, 103))
        epd.display(epd.getbuffer(image))
        if weather.get_humidity() is not None:
            draw.text((22, 105), weather.get_humidity(), font=font14, fill=0)

        bmp = Image.open(os.path.join(picdir, 'preciption.bmp'))  # preciption
        image.paste(bmp, (65, 103))
        epd.display(epd.getbuffer(image))
        draw.text((88, 105), get_preciption(), font=font14, fill=0)

        crop_image = image.crop([0, 0, 118, epd.width])
        image.paste(crop_image, (0, 0))
        epd.display(epd.getbuffer(image))


def display_weather_forecast():
    global random_bool

    LOGGER.info ('Forecast update')
    # epd.init(epd.lut_partial_update)
    # epd.Clear(0xFF)
    # epd.Clear(0xFF)  draw.line([(120, 5), (120, epd.width - 5)], fill=0, width=1)
    # time.sleep(2)

    if len(forecast) > 1:
        draw.rectangle((122, 32, epd.height, epd.width), fill=255)

        display_day(forecast[1], 150, 32, 140, 50, 140, 105)

        # Vertical Middle Line
        draw.line([(210, 35), (210, epd.width - 5)], fill=0, width=1)

        display_day(forecast[2], 240, 32, 230, 50, 230, 105)

        crop_image = image.crop([122, 32, epd.height, epd.width])
        image.paste(crop_image, (122, 32, epd.height, epd.width))
        epd.display(epd.getbuffer(image))
    else:
        LOGGER.warning('Weather Forecast List Empty')


def display_day(daycast, dx, dy, ix, iy, tx, ty):
    if daycast is not None:
        # draw.text((dx, dy), daycast.get_next_day() + ' (' + daycast.get_preciption() + ')', font=font14, fill=0)
        draw.text((dx, dy), daycast.get_next_day(), font=font14, fill=0)
        # image
        bmp = Image.open(get_weather_image(daycast.get_condition()))
        image.paste(bmp, (ix, iy))
        draw.text((tx, ty), daycast.get_low() + "-" + daycast.get_temp() + '°c', font=font14, fill=0)
        epd.display(epd.getbuffer(image))


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
    # schedule.every().minutes.at(':00').do(job_queue.put, (every_sec, []))
    schedule.every(30).seconds.do(job_queue.put, (every_sec, []))

    # Update weather every 13 mins once
    schedule.every(14).minutes.do(run_weather_thread, (call_weather_api, [location]))
    schedule.every(15).minutes.do(job_queue.put, (display_weather_main, []))

    # Update weather every 1 hour once
    schedule.every().hour.at(':00').do(run_weather_thread, (call_weather_forecast, [location]))
    schedule.every().hour.at(':02').do(job_queue.put, (display_weather_forecast, []))

    # Update day info every day starts
    schedule.every(15).day.at('00:00').do(job_queue.put, (display_date_info, []))


def welcome_screen():
    global image
    global draw

    LOGGER.info("welcome screen")
    clear_display()
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    draw.text((80, 0), 'Welcome', font=fontTemp18, fill=0)
    draw.text((10, 50), '2.9" epaper display', font=fontTemp18, fill=0)

    epd.display(epd.getbuffer(image))


# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    location = DEFAULT_LOC_UUID
    if len(sys.argv) > 1:
        location = sys.argv[1]

    random_bool = False

    try:
        LOGGER.info("Initializing Display")
        welcome_screen()

        worker_thread = threading.Thread(target=worker_main)
        worker_thread.start()

        call_apis_async(location)

        display_elink()

        add_scheduler(location)

        while 1:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        epd2in9.epdconfig.module_exit()
        exit()

