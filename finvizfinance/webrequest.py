import requests
from bs4 import BeautifulSoup

def webScrap(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    website = requests.get(url, headers=headers)
    soup = BeautifulSoup(website.text, 'lxml')
    return soup