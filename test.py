from aiohttp import ClientSession
import asyncio
import time
import requests
import datetime

# async call
async def fetch(url):
    async with ClientSession() as s, s.get(url) as res:
        ret = await res.read()
        print (ret)
        return ret

async def get():
    await asyncio.gather(*map(fetch, weather_url))

# sync call
def fetch_sync(url):
    ret = requests.get(url)
    print (ret.json())
    return ret.json()

weather_url = 'http://localhost:8080/forecast/weather'
print ('started')
start = time.time();


#asyncio.run(fetch(weather_url))
#fetch_sync(weather_url)
end = time.time()
print(f"Time Taken {end - start}")

print (datetime.datetime.today().weekday(), ' ', datetime.datetime.now().hour, ' ', datetime.datetime.now().minute)
