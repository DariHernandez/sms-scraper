import os
import bs4
import json
import requests
import globals
from config import Config
from logs import logger
from concurrent.futures import ThreadPoolExecutor

# Scraping variables
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36", 
}
home_page = "https://receive-smss.com/"

# Get credentials from config file
credentials = Config ()
threads_num = credentials.get ("threads_num")
debug_mode = credentials.get ("debug_mode") 

# History file
history_path = os.path.join (os.path.dirname (__file__), "history.json")
history_obj = Config (history_path)
globals.history = history_obj.get ("history")

# Initial debug
logger.info ("")

# Setup pool of threads
excecutor = ThreadPoolExecutor(max_workers=threads_num + 1)

def thread_killer ():
    """Requests a user input for kill an threads"""
    while True:
        user_input = input ("\nThreads running. press 'q' to end the program.\n\n")
        if 'q' in user_input.lower():
            globals.running = False
            return None
        else:
            continue

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

def send_message (num):
    """Get all message for the current number, and send to the API"""

    num_formated = num.replace('sms/', '')

    # End thread 
    if not globals.running:
        return None

    num_page = f"{home_page}{num}/"
    res = requests.get (num_page, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    selector_row = ".table.table-bordered.wrptable.tbdif > tbody > tr"
    rows = soup.select (selector_row)
    for row_index in range(1, len(rows) + 1):

        # End thread 
        if not globals.running:
            return None

        # Get message data
        selector_from_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(1)"
        selector_body_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(2)"
        selector_date_sms = f"{selector_row}:nth-child({row_index}) > td:nth-child(3)"

        from_sms = soup.select (selector_from_sms)[0].getText().replace("\n", "")
        body_sms = soup.select (selector_body_sms)[0].getText().replace("\n", "")
        date_sms = soup.select (selector_date_sms)[0].getText().replace("\n", "")

        row_data = [num_formated, from_sms, body_sms]
        if not row_data in globals.history:
            # Save data and send to the api
            globals.history.append (row_data)
            logger.info (f"Number: {num_formated} | From: {from_sms} | Body: {body_sms} | Date: {date_sms}")
        else:
            # Skip duplicates
            break

    # Update history file when table extraction ends
    history_obj.update ("history", globals.history)    

if __name__ == "__main__":

    # Run therad killer
    if debug_mode:
        excecutor.submit(thread_killer)

    # Run thread for each number
    nums = get_nums ()
    for num in nums[0:2]:
        excecutor.submit (send_message, num)

    # Message for end the program
    if debug_mode:
        print("\nWeb scraping ended. Press 'q' to close the program.\n\n")