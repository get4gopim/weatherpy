# This is a sample Python script.

import WeatherInfo
import RateInfo

import json
from collections import namedtuple
import requests

weather_url = 'http://localhost:8080/forecast/weather'
gold_rate_url = 'http://localhost:8080/forecast/gold'

def get_weather():
    weather_response = requests.get(weather_url)
    print(weather_response)

    weather_info = WeatherInfo.WeatherInfo(0, 0, 0, "00:00", "", "")

    if weather_response.status_code == 200:
        weather_json = weather_response.text
        #print(weather_json)

        x = json.loads(weather_json, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        #print('Temp: ', x.temperature, ' Date: ', x.asOf)

        weather_info = WeatherInfo.WeatherInfo(x.temperature, x.low, x.high, x.asOf, x.currentCondition, x.location)
    else:
        print('WeatherInfo API returned an error.')

    return weather_info

def get_gold_rate():
    gold_rate_response = requests.get(gold_rate_url)
    print(gold_rate_response)

    rate_info = RateInfo.RateInfo(0, 0, 0.0)

    if gold_rate_response:
        gold_json = gold_rate_response.text
        #print(gold_json)

        x = json.loads(gold_json, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
        #print('Rate Card: ', x.goldRate22, ' Silver: ', x.silver)

        rate_info = RateInfo.RateInfo(x.goldRate22, x.goldRate24, x.silver)
    else:
        print('GoldRateInfo API Returned an error.')

    return rate_info
