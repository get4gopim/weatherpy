# This is a sample Python script.

import WeatherInfo
import RateInfo

import json
from collections import namedtuple
import requests
import asyncio

from aiohttp import ClientSession

weather_url = 'http://localhost:8080/forecast/weather'
gold_rate_url = 'http://localhost:8080/forecast/gold'

class AsyncWeatherCast:
    def __init__(self, ):
        self.__weather_info = weather_info


# async call
async def get_weather():
    global weather_info
    async with ClientSession() as s, s.get(weather_url) as response:
        ret = await response.read()
        x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        weather_info = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asOf, x.currentCondition, x.location)
        return weather_info

def asnyc_aiohttp_get_all():
    """
    performs asynchronous get requests
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_weather())

async def get_gold_rate():
    global rate_info
    async with ClientSession() as s, s.get(gold_rate_url) as response:
        ret = await response.read()
        x = json.loads(ret, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        rate_info = RateInfo.RateInfo(x.goldRate22, x.goldRate24, x.silver)
        return rate_info

if __name__ == '__main__':
    weather_info = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "")
    asyncio.run(get_gold_rate())
    print('details: ', rate_info.get_gold22(), ' ', rate_info.get_silver())