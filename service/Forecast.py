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
from service import MongoCloudService


query_str = {'attr_name': 'aws_weather_uri'}
default_url = 'https://rryf2kws46.execute-api.ap-south-1.amazonaws.com/dev'
weather_url = '/api/v1/weather'
gold_rate_url = '/api/v1/gold'
fuel_rate_url = '/api/v1/fuel'

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)


def get_base_aws_uri():
    aws_base_url = MongoCloudService.get_attr_config(query_str)
    if aws_base_url is None:
        aws_base_url = default_url
    return aws_base_url


def get_weather_sync(location):
    url = get_base_aws_uri() + weather_url + '/' + location
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
    print(weather_json)
    x = json.loads(weather_json, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    weather_info = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asof, x.condition, x.location, x.preciption)
    weather_info.set_humidity(x.humidity)
    return weather_info


async def get_weather(future, location):
    start = time.time()

    url = get_base_aws_uri() + weather_url + '/' + location
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


def parse_weather_forecast(response):
    w_list = json.loads(response)
    list_days = []

    for x in w_list:
        info = dict_to_object(x)
        # print(info)
        day = WeatherForecast.WeatherForecast(info.next_day, info.temperature, info.low, info.condition, info.preciption)
        day.set_humidity(info.humidity)
        list_days.append(day)

    return list_days


def dict_to_object(d):
    for k,v in d.items():
        if isinstance(v, dict):
            d[k] = dict_to_object(v)
    return namedtuple('WeatherForecast', d.keys())(*d.values())


async def get_weather_forecast(future, location):
    start = time.time()

    url = get_base_aws_uri() + weather_url + '/' + location + '/forecast'
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


def parse_gold_info(response):
    print(response)
    x = json.loads(response, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    info = RateInfo.RateInfo(x.gold22, x.gold24, x.silver, x.date, x.lastUpdated)
    return info


async def get_gold_price(future):
    start = time.time()
    info = None
    url = get_base_aws_uri() + gold_rate_url
    LOGGER.info(url)

    try:
        async with ClientSession() as session:
            html = await fetch(session, url)
            LOGGER.info(f'gold content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_gold_info(html)
            LOGGER.info(f'gold parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Gold API : {repr(ex)}')
        info = RateInfo.RateInfo('0', '0', '0.0', "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to connect Gold API : {repr(ex)}')
        info = RateInfo.RateInfo('0', '0', '0.0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Gold Time Taken {time.time() - start}')
    future.set_result(info)


def parse_fuel_info(response):
    print(response)
    x = json.loads(response, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    info = FuelInfo.FuelInfo(x.petrol, x.diesel, x.date, x.lastUpdated)
    return info


async def get_fuel_price(future):
    start = time.time()
    info = None
    url = get_base_aws_uri() + fuel_rate_url
    LOGGER.info(url)

    try:
        async with ClientSession() as session:
            html = await fetch(session, url)
            LOGGER.info(f'fuel content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_fuel_info(html)
            LOGGER.info(f'fuel parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Fuel API : {repr(ex)}')
        info = FuelInfo.FuelInfo('0', '0', "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to connect Weather API : {repr(ex)}')
        info = FuelInfo.FuelInfo('0', '0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Fuel Time Taken {time.time() - start}')
    future.set_result(info)


def callback(future):
    print(future.result())


def call_weather_api(location):
    LOGGER.info("call_weather_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_weather(f1, location)]

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


def call_gold_api():
    LOGGER.info("call_weather_forecast")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_gold_price(f1)]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return f1.result()


def call_fuel_api():
    LOGGER.info("call_fuel_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_fuel_price(f1)]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return f1.result()


if __name__ == '__main__':
    call_weather_api('thalambur')
    # call_weather_forecast('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d')
    # call_gold_api()
    # call_fuel_api()