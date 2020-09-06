# Python Forecast Application designed for LCD 20x4 and 16x2 I2C Display

Tested this application in Raspberry Pi Zero W, Raspberry Pi 3B+, Raspberry Pi 4B Models.
It can also work on any linux based single borad coomputer.

The 20x4 display has the following informations on each line on the LCD.
- Current Date, Day of th week and time (hour:min:sec)
- Temperature & Preciption of weather data
- Gold & Fuel Rate on the line 3 and 4

The 16x2 will display has the informations on each line on the LCD.
- Current Date and time (hour:min:sec)
- Temperature,Preciption of weather data, Location and Gold Silver rates

More info: https://github.com/get4gopim/weatherpy/wiki

## Required Python Libraries
For I2C communication i2c tools is required, install using the below command:
sudo apt install i2c-tools

The following libraries can be installed via a sudo apt install python command or pip install command
- python3-smbus
- python3-aiohttp
- python3-bs4
- python3-schedule

> Example: sudo apt install python3-aiohttp

## Startup Script

To run this when pi boots add the below command in crontab command. To open crontab use this:

```
sudo crontab -e
```

Choose your editior if it asked.

Add the below script at the end.

```
@reboot /home/pi/lcd_start.sh > /home/pi/script.log 2>&1 &
```

The script file lcd_start.sh can be found in the script directory of the checkout weatherpy project.
