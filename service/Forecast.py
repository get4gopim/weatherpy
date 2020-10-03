# REST Client Consumer

import json
import logging
import os
import asyncio
import async_timeout
import requests
import time

from model import WeatherInfo, WeatherForecast, RateInfo, FuelInfo
from collections import namedtuple
from aiohttp import ClientSession, ClientConnectorError, TCPConnector


base_url = 'https://rryf2kws46.execute-api.ap-south-1.amazonaws.com'
weather_url = '/dev/api/v1/weather'
gold_rate_url = '/dev/api/v1/gold'

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)


def get_weather(location):
    url = base_url + weather_url + '/' + location
    print(url)
    weather_response = requests.get(url)
    print(weather_response)

    weather_info = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "", "")

    if weather_response.status_code == 200:
        weather_json = weather_response.text
        print(weather_json)
        weather_info = parse_weather(weather_json)
    else:
        print('WeatherInfo API returned an error.')

    return weather_info


async def fetch(session, url):
    try:
        async with async_timeout.timeout(30):
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f'Response Status {response.status} is not OK')
    except asyncio.TimeoutError as ex:
        LOGGER.error(f'Unable to connect remote API : {url} - {repr(ex)}')
        raise ex


def parse_weather(weather_json):
    print (weather_json)
    x = json.loads(weather_json, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    weather_info = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asof, x.condition, x.location, x.preciption)
    weather_info.set_humidity(x.humidity)
    return weather_info


async def get_weather_async(future, location):
    start = time.time()

    url = base_url + weather_url + '/' + location
    info = None
    LOGGER.info(url)

    try:
        async with ClientSession() as session:
            html = await fetch(session, url)
            LOGGER.info(f'weather content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_weather(html)
            LOGGER.info(f'weather parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to parse Weather API : {repr(ex)}')
        LOGGER.error(ex)
        info = WeatherInfo.WeatherInfo('0', "0", "0", "00:00", "", "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to parse Weather API :- {repr(ex)}')
        LOGGER.error(ex)
        info = WeatherInfo.WeatherInfo('0', "0", "0", "00:00", "", "", "")
        info.set_error(ex)

    future.set_result(info)


def parse_weather_forecast(weather_json):
    # print(weather_json)
    list = json.loads(weather_json)
    # print(list)

    list_days = []
    for text in list:
        print(text)
        x = json.loads(text, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        info = WeatherForecast.WeatherForecast(x.next_day, x.temperature, x.low, x.condition, x.preciption)
        list_days.append(info)

    return list_days


async def get_weather_forecast(future, location):
    start = time.time()

    url = base_url + weather_url + '/' + location + '/forecast'
    info = None
    LOGGER.info(url)

    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            html = await fetch(session, url)
            LOGGER.info(f'weather content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_weather_forecast(html)
            LOGGER.info(f'weather parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to parse Weather forecast API : {repr(ex)}')
        info = []
    except BaseException as ex:
        LOGGER.error(f'Unable to parse Weather forecast API : {repr(ex)}')
        info = []

    future.set_result(info)


def callback(future):
    print(future.result())


def call_weather_api(location):
    LOGGER.info("call_weather_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_weather_async(f1, location)]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return f1.result()


def call_weather_forecast(location):
    LOGGER.info("call_weather_forecast")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_weather_forecast(f1, location)]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return f1.result()


if __name__ == '__main__':
    # call_weather_api('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d')
    call_weather_forecast('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d')