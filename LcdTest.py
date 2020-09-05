import lcddriver_16x2
import lcddriver

import time

# mylcd = lcddriver_16x2.lcd()
mylcd = lcddriver.lcd()

while True:
    print ("LCD Display Starts ... ")
    mylcd.lcd_clear()
    mylcd.lcd_display_string("Hello World", 1)
    mylcd.lcd_display_string("Testing LCD", 2)
    time.sleep(1)