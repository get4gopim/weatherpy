#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'weatherpy/images')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'weatherpy/fonts')

import logging
from epddriver2in9 import epd2in9
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)


def disp_img():
    logging.info("4.read bmp file on window")
    bmp = Image.open(os.path.join(picdir, 'sun.bmp'))
    time_image.paste(bmp, (30, 5))
    # epd.display(epd.getbuffer(time_image))
    # time.sleep(2)

    time_draw.text((5, 20), 'Hi', font=font14, fill=0)
    time_draw.text((5, 40), '29', font=fontHiLow, fill=0)

    bmp = Image.open(os.path.join(picdir, 'thermo_sun.bmp'))
    time_image.paste(bmp, (30, 60))
    time_draw.text((50, 60), '27', font=fontTemp, fill=0)
    time_draw.text((75, 60), '°c', font=font8, fill=0)

    time_draw.text((100, 20), 'Lo', font=font14, fill=0)
    time_draw.text((100, 40), '23', font=fontHiLow, fill=0)

    time_draw.text((5, 82), 'Mostly Cloudy', font=font14, fill=0)
    # time_draw.text((10, 105), 'Humidity : 84%', font=font14, fill=0)

    bmp = Image.open(os.path.join(picdir, 'humidity_solid.bmp'))
    time_image.paste(bmp, (5, 103))
    epd.display(epd.getbuffer(time_image))
    time_draw.text((25, 105), '84%', font=font14, fill=0)

    bmp = Image.open(os.path.join(picdir, 'preciption.bmp')) # preciption
    time_image.paste(bmp, (65, 103))
    epd.display(epd.getbuffer(time_image))
    time_draw.text((85, 105), '20%', font=font14, fill=0)

    # Vertical Middle Line
    time_draw.line([(120, 5), (120, epd.width-5)], fill=0, width=1)

    # Date & Time
    time_draw.text((125, 5), time.strftime("%b %d, %A"), font=font12, fill=0)
    # time_draw.text((185, 0), time.strftime("%b %d"), font=font14, fill=0)
    # # Horizontal Line with Padding 5
    # time_draw.line([(180, 18), (230, 18)], fill=0, width=2)
    # time_draw.text((180, 20), time.strftime("%A"), font=font14, fill=0)
    # Horizontal Line with Padding 5
    time_draw.line([(125, 30), (epd.height-5, 30)], fill=0, width=1)
    time_draw.text((250, 5), time.strftime('%H:%M'), font=fontTime, fill=0)

def disp_img2():
    time_draw.text((145, 32), 'Wed', font=font14, fill=0)
    # image
    bmp = Image.open(os.path.join(picdir, 'w_rain.bmp'))
    time_image.paste(bmp, (140, 50))
    epd.display(epd.getbuffer(time_image))
    # time.sleep(2)
    time_draw.text((140, 105), '22-29°c', font=font14, fill=0)
    time_draw.text((230, 105), '23-39°c', font=font14, fill=0)

    # Vertical Middle Line
    time_draw.line([(210, 35), (210, epd.width - 5)], fill=0, width=1)

    time_draw.text((245, 32), 'Thu', font=font14, fill=0)
    # image
    bmp = Image.open(os.path.join(picdir, 'foggy.bmp'))
    time_image.paste(bmp, (230, 50))
    epd.display(epd.getbuffer(time_image))
    # time.sleep(2)


    # bmp = Image.open(os.path.join(picdir, 'haze.bmp'))
    # time_image.paste(bmp, (240, 50))
    # epd.display(epd.getbuffer(time_image))
    # time.sleep(2)

    # bmp = Image.open(os.path.join(picdir, 'foggy.bmp'))
    # time_image.paste(bmp, (250, 40))
    # epd.display(epd.getbuffer(time_image))
    # time.sleep(2)

try:
    logging.info("epd2in9 Demo")
    
    epd = epd2in9.EPD()
    logging.info("init and Clear")
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    time.sleep(2)

    font24 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 24)
    font18 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 18)
    # font14 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 12)
    font8 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)

    font14 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Light.ttf'), 14)
    font12 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Light.ttf'), 12)
    # fontTime = ImageFont.truetype('/home/pi/PycharmProjects/weatherpy/fonts/DjbGetDigital-6G5g.ttf', 20)
    fontHiLow= ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 18)
    fontTime = ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 22)
    fontTemp = ImageFont.truetype(os.path.join(fontdir, 'digital-7.ttf'), 26)
    fontTemp18 = ImageFont.truetype(os.path.join(fontdir, 'ThunderDemo.ttf'), 36)

    # # Drawing on the Horizontal image
    # logging.info("1.Drawing on the Horizontal image...")
    # Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Himage)
    # draw.text((35, 30), 'Welcome Cresto', font=fontTemp18, fill=0)
    # draw.text((10, 20), '2.9inch e-Paper', font = font24, fill = 0)
    # draw.text((150, 0), u'微雪电子', font = font24, fill = 0)
    # draw.line((20, 50, 70, 100), fill = 0)
    # draw.line((70, 50, 20, 100), fill = 0)
    # draw.rectangle((20, 50, 70, 100), outline = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    # draw.line((140, 75, 190, 75), fill = 0)
    # draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    # draw.rectangle((80, 50, 130, 100), fill = 0)
    # draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(5)
    #
    # Drawing on the Vertical image
    # logging.info("2.Drawing on the Vertical image...")
    # Limage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Limage)
    # draw.text((2, 0), 'hello world', font = font18, fill = 0)
    # draw.text((2, 20), '2.9inch epd', font = font18, fill = 0)
    # draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
    # draw.line((10, 90, 60, 140), fill = 0)
    # draw.line((60, 90, 10, 140), fill = 0)
    # draw.rectangle((10, 90, 60, 140), outline = 0)
    # draw.line((95, 90, 95, 140), fill = 0)
    # draw.line((70, 115, 120, 115), fill = 0)
    # draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
    # draw.rectangle((10, 150, 60, 200), fill = 0)
    # draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
    # epd.display(epd.getbuffer(Limage))
    # time.sleep(2)
    #
    # logging.info("3.read bmp file")
    # Himage = Image.open(os.path.join(picdir, 'cloudy_sun.bmp'))
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(2)
    #


    
    # partial update
    logging.info("5.show time")
    epd.init(epd.lut_partial_update)    
    epd.Clear(0xFF)

    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    # time_draw.text((130, 30), time.strftime('%H:%M:%S'), font=font24, fill=0)
    # time_draw.rectangle((121, 10, 290, 125), outline=0, width=2)

    disp_img()
    disp_img2()

    # num = 0
    # while (True):
    #     time_draw.rectangle((0, 0, 120, 30), fill = 255)
    #     time_draw.text((0, 0), time.strftime('%H:%M:%S'), font = font24, fill = 0)
    #     newimage = time_image.crop([0, 0, 120, 30])
    #     time_image.paste(newimage, (0,0))
    #     epd.display(epd.getbuffer(time_image))
    #     time.sleep(0.2)
    #     num = num + 1
    #     if num == 1000:
    #         break
            
    # logging.info("Clear...")
    # epd.init(epd.lut_full_update)
    # epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
    epd.Dev_exit()
    
except IOError as e:
    logging.error(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in9.epdconfig.module_exit()
    exit()
