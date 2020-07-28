import requests
from bs4 import BeautifulSoup

"""
Module:         util
Description:    General function for the package.
Author:         Tianning Li
"""

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

def webScrap(url):
    """Scrap website.

    Parameters:
        url(str): website
    Returns:
        soup(beautiful soup): website html
    """
    website = requests.get(url, headers=headers)
    soup = BeautifulSoup(website.text, 'lxml')
    return soup

def imageScrap(url, ticker, out_dir):
    """scrap website and download image

    Parameters:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    r = requests.get(url, stream=True, headers=headers)
    if r.status_code == 200:
        r.raw.decode_content = True
        if len(out_dir) != 0:
            out_dir +='/'
        f = open('{}{}.jpg'.format(out_dir, ticker), "wb")
        f.write(r.content)
        f.close()
        print('Done')
    else:
        print('Error...')
        print(r.status_code)

def numberCovert(num):
    """covert number(str) to number(float)

    Parameters:
        num(str): number of string
    Return:
        num(float): number of string
    """
    if num == '-':
        return None
    elif num[-1] == '%':
        return float(num[:-1]) / 100
    elif num[-1] == 'B':
        return float(num[:-1]) * 1000000000
    elif num[-1] == 'M':
        return float(num[:-1]) * 1000000
    elif num[-1] == 'K':
        return float(num[:-1]) * 1000
    else:
        return float(''.join(num.split(',')))