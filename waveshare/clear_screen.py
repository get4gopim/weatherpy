from waveshare import epd2in13

try:
    print ('Clearing ...')
    epd = epd2in13.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd.Clear(0xFF)

    epd.sleep()

except BaseException as ex:
    exit()