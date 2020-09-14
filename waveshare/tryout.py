from epddriver2in13 import epd2in13
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import traceback
import os


def welcome_date_month():
    current_time = datetime.datetime.now()
    day = current_time.strftime("%d")
    month = current_time.strftime("%b")
    week_day = current_time.strftime("%A")
    year = current_time.strftime("%Y")

    if current_time.month == 9 and current_time.weekday() in [2, 3, 5]:
        month = current_time.strftime("%b")

    # time = current_time.strftime('%H:%M:%S').rjust(12, ' ')
    # Format: 29 August Sunday, 22 Sep Wednesday
    wel_date = str(day + ' ' + week_day + ' ' + year)
    return wel_date


def weekday():
    current_time = datetime.datetime.now()
    return current_time.strftime("%A")

def day_month():
    current_time = datetime.datetime.now()
    return current_time.strftime("%b %d")

def get_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%H:%M')

try:
    font_path = '../fonts/CarterOne-Regular.ttf'
    assert os.path.isfile(font_path)

    epd = epd2in13.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd.Clear(0xFF)

    # Drawing on the image
    image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    draw.rectangle([(0, 0), (249, 121)], outline=0) # draw rectangle

    font15 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 20)
    font8 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 8)
    fontWeather = ImageFont.truetype('/usr/share/fonts/truetype/google/KaushanScript-Regular.ttf', 16)
    fontBangers = ImageFont.truetype('/usr/share/fonts/truetype/google/Bangers-Regular.ttf', 18) # Bold Capital
    fontPacific = ImageFont.truetype('/usr/share/fonts/truetype/google/Pacifico-Regular.ttf', 16) # Bold

    fontCater20 = ImageFont.truetype('/usr/share/fonts/truetype/google/CarterOne-Regular.ttf', 20)

    fontTemperature = ImageFont.truetype('../fonts/CarterOne-Regular.ttf', 24)  # Bold
    fontWeekDay = ImageFont.truetype('../fonts/Roboto-Black.ttf', 18)
    fontTime = ImageFont.truetype('../fonts/Roboto-Black.ttf', 16)
    fontLocation = ImageFont.truetype('../fonts/Roboto-Regular.ttf', 18)

    # Vertical Middle Line
    draw.line([(160, 5), (160, 118)], fill=0, width=0)

    draw.text((10, 50), "Thalambur", font=fontLocation, fill=0)

    # weather bmp file
    print("read bmp file")
    weather_img = Image.open('../images/cloudy.bmp')
    image.paste(weather_img, (180, 5))

    # Horizontal Line with Padding 5
    draw.line([(165, 80), (245, 80)], fill=0, width=0)

    draw.text((170, 50), "27~32°c", font=fontTemperature, fill=0)
    draw.text((170, 80), weekday(), font=fontTime, fill=0)
    draw.text((180, 100), day_month(), font=fontTime, fill=0)

    epd.display(epd.getbuffer(image))
    time.sleep(2)

    # # partial update
    print("Show time")
    # epd.init(epd.PART_UPDATE)
    # epd.Clear(0xFF)
    # time_image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
    # time_draw = ImageDraw.Draw(time_image)
    #
    # while True:
    #     draw.rectangle((5, 5, 90, 50), fill=255)
    #     draw.text((10, 10), get_time(), font=fontCater20, fill=0)
    #     newimage = time_image.crop([5, 5, 90, 50])
    #     image.paste(newimage, (0, 0))
    #     epd.displayPartial(epd.getbuffer(image))
    #     time.sleep(60)

except BaseException as ex:
    print('traceback.format_exc():\n%s', traceback.format_exc())
    exit()