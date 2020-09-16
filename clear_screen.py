from epddriver2in9 import epd2in9

try:
    print ('Clearing ...')
    epd = epd2in9.EPD()
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    epd.Clear(0xFF)

    epd.sleep()

except BaseException as ex:
    exit()