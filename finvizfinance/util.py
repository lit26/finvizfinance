"""
.. module:: util
   :synopsis: General function for the package.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",  
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}
session = requests.Session()

proxy_dict = None
timeout_value = 10
_session_primed = False


def set_proxy(proxies):
    global proxy_dict
    proxy_dict = proxies


def set_timeout(timeout):
    global timeout_value
    timeout_value = timeout


def _prime_session():
    """Prime the session by visiting the homepage.
    """
    global _session_primed
    if not _session_primed:
        try:
            session.get(
                "https://finviz.com/",
                headers=headers,
                timeout=timeout_value,
                proxies=proxy_dict
            )
            _session_primed = True
        except Exception:
            # If priming fails, continue anyway - might work without it
            pass


def web_scrap(url, params=None, prime_session=False):
    """Scrap website.

    Args:
        url(str): website
        params(dict): request parameters
        prime_session(bool): if True, visit homepage first to prime session cookies
    Returns:
        soup(beautiful soup): website html
    """
    if prime_session:
        _prime_session()
    
    try:
        request_headers = headers.copy()
        if "screener.ashx" in url:
            request_headers["Referer"] = "https://finviz.com/"
            request_headers["Sec-Fetch-Site"] = "same-origin"
            request_headers["Sec-Fetch-Mode"] = "navigate"
        
        website = session.get(
            url, params=params, headers=request_headers, timeout=timeout_value, proxies=proxy_dict
        )
        website.raise_for_status()
        
        if len(website.content) == 0:
            raise requests.exceptions.HTTPError(
                f"Empty response from {url}."
            )
        
        # Handle Brotli compression manually if needed
        content_encoding = website.headers.get('Content-Encoding', '').lower()
        if content_encoding == 'br' and BROTLI_AVAILABLE:
            try:
                # Manually decompress Brotli content
                decompressed = brotli.decompress(website.content)
                website._content = decompressed
                # Force re-encoding detection
                website.encoding = website.apparent_encoding or 'utf-8'
            except Exception:
                # If decompression fails, try to use text anyway
                pass
        
        # Check if response looks like HTML (basic check)
        # If content is still binary/garbled, it might be compressed
        response_text = website.text
        if len(response_text.strip()) == 0 or not response_text.strip().startswith(('<', '<!', '<html', '<HTML')):
            # Try to detect if it's still compressed
            if content_encoding == 'br' and not BROTLI_AVAILABLE:
                raise requests.exceptions.HTTPError(
                    f"Response is Brotli-compressed but 'brotli' package is not installed. "
                    "Install it with: pip install brotli"
                )
            elif content_encoding == 'br':
                # Already tried to decompress, but still not HTML
                raise requests.exceptions.HTTPError(
                    f"Failed to decompress Brotli response from {url}. "
                )
            else:
                raise requests.exceptions.HTTPError(
                    f"Empty or invalid HTML response from {url}."
                )
        
        soup = BeautifulSoup(response_text, "lxml")
        return soup
    except requests.exceptions.HTTPError as err:
        raise requests.exceptions.HTTPError(f"HTTP error for URL {url}: {err}")
    except requests.exceptions.Timeout as err:
        raise requests.exceptions.Timeout(f"Timeout for URL {url}: {err}")


def image_scrap(url, ticker, out_dir):
    """scrap website and download image

    Args:
        url(str): website (image)
        ticker(str): output image name
        out_dir(str): output directory
    """
    try:
        r = session.get(url, stream=True, headers=headers, timeout=timeout_value, proxies= proxy_dict)
        r.raise_for_status()
        r.raw.decode_content = True
        if len(out_dir) != 0:
            out_dir += "/"
        f = open("{}{}.jpg".format(out_dir, ticker), "wb")
        f.write(r.content)
        f.close()
    except requests.exceptions.HTTPError as err:
        raise Exception(err)
    except requests.exceptions.Timeout as err:
        raise Exception(err)


def scrap_function(url):
    """Scrap forex, crypto information.

    Args:
        url(str): website
    Returns:
        df(pandas.DataFrame): performance table
    """
    soup = web_scrap(url)
    table = soup.find("table", class_="groups_table")
    rows = table.find_all("tr")
    table_header = [i.text.strip() for i in rows[0].find_all("th")][1:]
    frame = []
    rows = rows[1:]
    num_col_index = [i for i in range(2, len(table_header))]
    for row in rows:
        cols = row.find_all("td")[1:]
        info_dict = {}
        for i, col in enumerate(cols):
            if i not in num_col_index:
                info_dict[table_header[i]] = col.text
            else:
                info_dict[table_header[i]] = number_covert(col.text)
        frame.append(info_dict)
    return pd.DataFrame(frame)


def image_scrap_function(url, chart, timeframe, urlonly):
    """Scrap forex, crypto information.

    Args:
        url(str): website
        chart(str): choice of chart
        timeframe (str): choice of timeframe(5M, H, D, W, M)
        urlonly (boolean):  choice of downloading chart
    """
    if timeframe == "5M":
        url += "m5"
    elif timeframe == "H":
        url += "h1"
    elif timeframe == "D":
        url += "d1"
    elif timeframe == "W":
        url += "w1"
    elif timeframe == "M":
        url += "mo"
    else:
        raise ValueError("Invalid timeframe.")

    soup = web_scrap(url)
    content = soup.find("div", class_="container")
    imgs = content.find_all("img")
    for img in imgs:
        website = img["src"]
        name = website.split("?")[1].split("&")[0].split(".")[0]
        chart_name = name.split("_")[0]
        if chart.lower() == chart_name:
            charturl = "https://finviz.com/" + website
            if not urlonly:
                image_scrap(charturl, name, "")
            return charturl
        else:
            continue


def number_covert(num):
    """Convert number(str) to number(float)

    Args:
        num(str): number as a string
    Return:
        num(float, str, or None): number converted to float, original string if conversion fails, or None
    """
    if not num or num == "-":  # Check if the string is empty or is "-"
        return None
    num = num.strip()  # Remove any surrounding whitespace
    
    # Check for date-like patterns (e.g., "Nov 24/a", "Jan 15", etc.)
    # These typically contain month abbreviations and slashes
    month_abbrevs = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if "/" in num and any(month in num for month in month_abbrevs):
        # Likely a date string, return as-is
        return num
    
    try:
        if num[-1] == "%":
            return float(num[:-1]) / 100
        elif num[-1] == "B":
            return float(num[:-1]) * 1000000000
        elif num[-1] == "M":
            return float(num[:-1]) * 1000000
        elif num[-1] == "K":
            return float(num[:-1]) * 1000
        else:
            return float(num.replace(",", ""))  # Remove commas and convert to float
    except (ValueError, IndexError):
        # If conversion fails (e.g., date strings, text fields), return the original string
        return num


def format_datetime(date_str):
    if date_str.lower().startswith("today"):
        today = date.today()
        time_str = date_str.split()[1]

        hour, minute = map(int, time_str[:-2].split(":"))
        ampm = time_str[-2:]

        if ampm.lower() == "pm" and hour != 12:
            hour += 12
        return datetime(today.year, today.month, today.day, hour, minute)
    else:
        return datetime.strptime(date_str, "%b-%d-%y %I:%M%p")


def progress_bar(page, total):
    bar_len = 30
    filled_len = int(round(bar_len * page / float(total)))
    bar = "#" * filled_len + "-" * (bar_len - filled_len)
    sys.stdout.write("[Info] loading page [{}] {}/{} \r".format(bar, page, total))
    sys.stdout.flush()
