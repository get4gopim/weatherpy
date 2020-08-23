import requests
import time
import asyncio
import aiohttp

async def fetch(session, url):
    """Execute an http call async
    Args:
        session: contexte for making the http call
        url: URL to call
    Return:
        responses: A dict like object containing http response
    """
    async with session.get(url) as response:
        resp = await response.json()
        print (resp)
        return resp

async def fetch_all(cities):
    """ Gather many HTTP call made async
    Args:
        cities: a list of string
    Return:
        responses: A list of dict like object containing http response
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for city in cities:
            tasks.append(
                fetch(
                    session,
                    f"https://geo.api.gouv.fr/communes?nom={city}&fields=nom,region&format=json&geometry=centr",
                )
            )
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

def run(cities):
    start = time.time();
    responses = asyncio.run(fetch_all(cities))
    end = time.time()
    print(f"Time Taken {end - start}")
    return responses

if __name__ == '__main__':
    cities = ["US", "Paris", "France", "Pantin", "Drancy", "Bobigny", "Bondy", "Gagny"]
    run(cities)