#!/bin/sh
echo "Starting LCD Script"

# echo "$JAVA_HOME/bin"

# network wait sleep time [if required]

#sleep 10

echo 'Starting python lcd script'

#location='49ceef3a36a9f805cdbf9fb01da64837d038f2256d4c3457dca28833422e0000' # Kolathur
location='4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d' # Thalambur
#location='kolathur+salem'

echo $location

#python3 /home/pi/workspace/weatherpy/16x2_lcd_main.py $location > /home/pi/i2c_lcd.log 2>&1 &
python3 /home/pi/workspace/weatherpy/20x4_lcd_main.py $location > /home/pi/i2c_lcd.log 2>&1 &
#python3 /home/pi/workspace/weatherpy/2in13_epaper_main.py $location > /home/pi/i2c_lcd.log 2>&1 &

# sleep and try the below after 10 mins to pickup the changes from git

sleep 600

echo 'Git fetch update will start'

#cd /home/pi/workspace/weatherpy
#git fetch --all
#git reset --hard origin/master
#git pull origin master

echo 'Git fetch & update completed'

echo 'Done'