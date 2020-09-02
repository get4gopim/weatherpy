import aiohttp
import asyncio
import async_timeout
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import time

content_area_class = 'entry-content'

async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def soup_d(html, display_result=False):
    soup = BeautifulSoup(html, 'html.parser')
    if display_result:
        print(soup.prettify())
    return soup

async def extract_text(html):
    soup = await soup_d(html)
    content_area = soup.find("div", {"class": content_area_class})
    text = content_area.text
    return text


blogpost_pattern = r'^/(?P<year>\d+){4}/(?P<month>\d+){2}/(?P<day>\d+){2}/(?P<slug>[\w-]+)/$'

async def match_path(path):
    pattern = re.compile(blogpost_pattern)
    matching = pattern.match(path)
    if  matching is None:
        return False, None
    return True, matching


async def process_string(string):
    string = string.replace("\n", " ")
    string = string.replace("—", "")
    string = string.replace("|", "")
    string = string.replace("\n", " ")
    string = string.replace("\"", "")
    string = string.replace("\xa0", " ")
    string = string.replace("“", "")
    string = string.replace("”", "")
    string = string.replace("–", "")
    string = string.replace(".", "")
    string = string.replace("?", "")
    string = string.replace(",", "")
    string = string.replace("'ve", " have")
    #string = string.replace(".", " || PERIOD ||")
    #string = string.replace("?", " || QUESTION_MARK ||")
    return string.strip()


async def extract_local_links(html, root_domain, local_only=True):
    soup = await soup_d(html)
    href_tags = soup.find_all("a", href=True)
    links = [a['href'] for a in href_tags]
    if local_only:
        paths = []
        for x in links:
            if urlparse(x).netloc == root_domain:
                link = urlparse(x).path
                is_matching = await match_path(link)
                if is_matching[0]:
                    paths.append(link)
    return list(set(paths))



async def main(url):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        parsed_url = urlparse(url)
        root_domain = parsed_url.netloc
        domain = parsed_url.geturl() # includes trailing /
        #print(domain)
        html = await fetch(session, url)
        paths = await extract_local_links(html, root_domain)
        #print(paths)
        words = []
        for path in list(set(paths)):
            start_ = time.time()
            post_url  = domain + path
            new_html = await fetch(session, post_url)
            text = await extract_text(new_html)
            string = await process_string(text)
            sub_words = string.split()
            words += sub_words
            print(time.time() - start_, "seconds")
        word_freq = Counter(words)
        print("Entire request took", time.time()-start_time, "seconds")
        print(word_freq.most_common(10))



loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main('http://tim.blog'))
except:
    pass