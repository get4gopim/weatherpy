
import requests
import time
import asyncio

async def fetch_all(cities):
    start = time.time();
    responses = []
    with requests.session() as session:
        for city in cities:
            resp = session.get(f"https://geo.api.gouv.fr/communes?nom={city}&fields=nom,region&format=json&geometry=centr")
            print(resp.json())
            responses.append(resp.json())
    end = time.time()
    print (f"Time Taken {end - start}")
    return responses

def run(cities):
    responses = asyncio.run(fetch_all(cities))
    return responses

if __name__ == '__main__':
    cities = ["US", "Paris", "France", "Pantin", "Drancy", "Bobigny", "Bondy", "Gagny",
              "US", "Paris", "France", "Pantin", "Drancy", "Bobigny", "Bondy", "Gagny",
              "US", "Paris", "France", "Pantin", "Drancy", "Bobigny", "Bondy", "Gagny"]
    run(cities)
