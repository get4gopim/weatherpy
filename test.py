from aiohttp import ClientSession
from bs4 import BeautifulSoup

import asyncio
import time
import requests
import datetime


def get_monster_jobs():
    URL = 'https://www.monster.com/jobs/search/?q=Software-Developer&where=Australia'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='ResultsContainer')
    # print(results.prettify())

    job_elems = results.find_all('section', class_='card-content')
    for job_elem in job_elems:
        # Each job_elem is a new BeautifulSoup object.
        # You can use the same methods on it as you did before.
        title_elem = job_elem.find('h2', class_='title')
        company_elem = job_elem.find('div', class_='company')
        location_elem = job_elem.find('div', class_='location')
        if None in (title_elem, company_elem, location_elem):
            continue
        print(title_elem.text.strip())
        print(company_elem.text.strip())
        print(location_elem.text.strip())
        print()


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
