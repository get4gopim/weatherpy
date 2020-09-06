import logging
import os
import asyncio
import async_timeout
import time
import aiohttp

from model import FuelInfo, RateInfo, WeatherInfo
from utility import util

from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientConnectorError

weather_url = 'https://weather.com/en-IN/weather/today/l/4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d'
gold_url = 'http://www.livechennai.com/gold_silverrate.asp'
fuel_url = 'https://www.livechennai.com/petrol_price.asp'

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)


async def fetch(session, url):
    try:
        async with async_timeout.timeout(20):
            async with session.get(url) as response:
                return await response.text()
    except asyncio.TimeoutError as ex:
        LOGGER.error(f'Unable to connect remote API : {url} - {repr(ex)}')
        info = WeatherInfo.WeatherInfo('0', "0", "0", "00:00", "", "", "")
        info.set_error(ex)


async def get_weather(future):
    start = time.time()
    info = None

    try:
        async with ClientSession() as session:
            html = await fetch(session, weather_url)
            info = await parse_weather(html)
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Weather API : {repr(ex)}')
        info = WeatherInfo.WeatherInfo('0', "0", "0", "00:00", "", "", "")
        info.set_error(ex)

    LOGGER.info (f'Weather Time Taken {time.time() - start}')
    future.set_result(info)


async def get_gold_price(future):
    start = time.time()
    info = None
    try:
        async with ClientSession() as session:
            html = await fetch(session, gold_url)
            info = await parse_gold_info(html)
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Gold API : {repr(ex)}')
        info = RateInfo.RateInfo('0', '0', '0.0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Gold Time Taken {time.time() - start}')
    future.set_result(info)


async def get_fuel_price(future):
    start = time.time()
    info = None

    try:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, fuel_url)
            info = await parse_fuel_info(html)
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Fuel API : {repr(ex)}')
        info = FuelInfo.FuelInfo('0', '0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Fuel Time Taken {time.time() - start}')
    future.set_result(info)


async def parse_weather(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    seg_temp = soup.find_all('div', {'id' : 'WxuCurrentConditions-main-b3094163-ef75-4558-8d9a-e35e6b9b1034'})[0]
    # print(seg_temp.text)

    location = seg_temp.find('h1', class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--location--1Ayv3')
    # print(location.text)
    location = location.text
    idx = util.index_of(location, ' Weather')
    if idx > 0:
        location = location[0:idx]

    as_of = seg_temp.find('div',
                             class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--timestamp--1SWy5')
    # print(as_of.text)
    as_of = as_of.text
    idx = util.index_of(as_of, "as of ")
    idx_ist = util.index_of(as_of, " IST")
    if idx > 0:
        as_of = as_of[idx+6:idx_ist]

    temp = seg_temp.find('span',
                              class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--tempValue--3KcTQ')
    # print(temp.text)
    temp = temp.text
    if len(temp) > 2:
        temp = temp[0:2]

    condition = seg_temp.find('div',
                         class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--phraseValue--2xXSr')
    # print(condition.text)
    condition = condition.text

    high_low = seg_temp.find('div',
                              class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--tempHiLoValue--A4RQE')
    # print(high_low.text)
    high_low = high_low.text
    idx = util.index_of(high_low, "/")
    high = temp
    low = temp
    if idx > 0:
        high = high_low[0:idx]
        low = high_low[idx+1:len(high_low)]

    if high == '--':
        high = temp

    if len(high) > 2:
        high = high[0:2]

    if len(low) > 2:
        low = low[0:2]

    preciption = seg_temp.find('div',
                             class_='_-_-node_modules-@wxu-components-src-organism-CurrentConditions-CurrentConditions--precipValue--RBVJT')
    # print(preciption.text)
    if preciption is not None:
        preciption = preciption.text
    else:
        preciption = ''

    weatherInfo = WeatherInfo.WeatherInfo(temp, low, high, as_of, condition, location, preciption)
    weatherInfo.set_error(None)
    LOGGER.info(str(weatherInfo))

    return weatherInfo


async def parse_gold_info(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    table = soup.select('table.table-price').__getitem__(1)
    rows = table.find_all('tr')

    # print (last_updated)

    gold_date = str(rows[2].find_all('td')[0].text).strip()
    gold_24 = str(rows[2].find_all('td')[1].text).strip()
    gold_22 = str(rows[2].find_all('td')[3].text).strip()

    # print (gold_22 + " " + gold_24 + " " + gold_date)

    table = soup.select('table.table-price').__getitem__(3)
    rows = table.find_all("tr")

    silver_date = str(rows[1].find_all('td')[0].text).strip()
    silver = str(rows[1].find_all('td')[1].text).strip()

    # print (silver_date + " " + silver)

    last_updated = soup.find_all('p', class_='mob-cont')[0]
    last_updated = last_updated.text.strip()
    idx = util.index_of(last_updated, ":")
    if idx > 0:
        last_updated = last_updated[idx + 1:len(last_updated)]

    rate_info = RateInfo.RateInfo(gold_22, gold_24, silver, gold_date, last_updated)
    rate_info.set_error(None)
    LOGGER.info(str(rate_info))

    return rate_info


async def parse_fuel_info(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    table = soup.select("table#BC_GridView1").__getitem__(0)
    # print (table)

    rows = table.find_all("tr")
    fuel_date = rows[1].find_all('td')[0].text
    petrol_price = str(rows[1].find_all('td')[1].text).strip()

    table = soup.select("table#BC_GridView1").__getitem__(1)
    # print (table)

    rows = table.find_all("tr")
    fuel_date = rows[1].find_all('td')[0].text
    diesel_price = str(rows[1].find_all('td')[1].text).strip()

    table = soup.find_all('table', {'id': 'tableb'}).__getitem__(1)
    # print (table)
    rows = table.find_all("tr")
    # print(rows)
    last_updated = rows[0].find_all('td', {'id': 'subcell'})[0]
    last_updated = last_updated.find_all('div')[3]
    # print (last_updated.text)
    last_updated = last_updated.text
    idx = util.index_of(last_updated, 'from ')
    if idx > 0:
        last_updated = last_updated[idx + 5:len(last_updated)]

    fuel_info = FuelInfo.FuelInfo(petrol_price, diesel_price, fuel_date, last_updated)
    fuel_info.set_error(None)

    LOGGER.info(str(fuel_info))

    return fuel_info


# Testing Methods
def callback(future):
    print (future.result())


def test_async_future():
    start = time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()
    f2 = asyncio.Future()
    f3 = asyncio.Future()

    f1.add_done_callback(callback)
    f2.add_done_callback(callback)
    f3.add_done_callback(callback)

    tasks = [get_weather(f1), get_gold_price(f2), get_fuel_price(f3)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print ('\n\n')


if __name__ == '__main__':
    LOGGER.info ("Parser starts ...")

    test_async_future()