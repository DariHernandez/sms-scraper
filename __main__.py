import os
from config import Config
from logs import logger
import requests
import bs4

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36", 
}
home_page = "https://receive-smss.com/"
logger.info ("")
logger.info ("Running")

def get_nums ():
    """Returns the number list from home page"""

    # Requests to page
    logger.debug ("Getting home page...")
    res = requests.get (home_page, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    # Get numbers
    logger.debug ("Fetting number links...")
    valid_nums = []
    selector_nums = ".number-boxes > a"
    nums = soup.select (selector_nums)
    for num in nums:
        if "sms" in num.attrs["href"]:
            valid_nums.append (num.attrs["href"][1:])

    return valid_nums

def get_message (num):
    """Returns the list of message for the current number"""
    num_page = f"{home_page}{num}/"
    res = requests.get (num_page, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    selector_row = ".table.table-bordered.wrptable.tbdif > tbody > tr"
    rows = soup.select (selector_row)
    for row_index in range(1, len(rows) + 1):
        
        selector_from_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(1)"
        selector_body_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(2)"
        selector_date_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(3)"

        from_sms = soup.select (selector_from_sms)[0].getText().replace("\n", "")
        body_sms = soup.select (selector_body_sms)[0].getText().replace("\n", "")
        date_sms = soup.select (selector_date_sms)[0].getText().replace("\n", "")

        logger.info (f"\tFrom: {from_sms} | Body: {body_sms} | Date: {date_sms}")

def main (): 
    nums = get_nums ()
    for num in nums:
        logger.info (f"Number: {num.replace('sms/', '')}")
        messages = get_message (num)

if __name__ == "__main__":
    main()