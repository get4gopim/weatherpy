#!/bin/sh
echo "Starting LCD Script"

echo "$JAVA_HOME/bin"

# network wait sleep time [if required]

#sleep 10

echo 'Starting python lcd script'

python3 /home/pi/workspace/weatherpy/20x4_lcd_main.py > /home/pi/i2c_lcd.log 2>&1 &

# sleep and try the below after 10 mins to pickup the changes from git

sleep 600

echo 'Git fetch update will start'

cd /home/pi/workspace/weatherpy
git fetch --all
git reset --hard origin/master
git pull origin master

echo 'Git fetch & update completed'

echo 'Done'
