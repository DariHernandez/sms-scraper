import os
import bs4
import time
import hashlib
import requests
import globals
from config import Config
from logs import logger
from database.my_sql import MySQL
from concurrent.futures import ThreadPoolExecutor

# Scraping variables
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36", 
}
home_page = "https://receive-smss.com/"

# Setting credentials
credentials = Config ()
threads_num = credentials.get ("threads_num")
debug_mode = credentials.get ("debug_mode") 
loop_mode = credentials.get ("loop_mode")
wait_time = credentials.get ("wait_time")
api_key = credentials.get ("api_key")

# Database credentials
dbname = credentials.get ("dbname")
table = credentials.get ("table")
user = credentials.get ("user")
password = credentials.get ("password")
hostname = credentials.get ("hostname")

# Connect to database
database = MySQL(hostname, dbname, user, password)

# History file
history_path = os.path.join (os.path.dirname (__file__), "history.json")
history_obj = Config (history_path)
globals.history = history_obj.get ("history")
globals.ids = history_obj.get ("ids")

# Initial debug
logger.info ("")

def get_nums ():
    """Returns the number list from home page"""

    # Requests to page
    logger.debug ("Getting home page...")
    res = requests.get (home_page, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    # Get numbers
    logger.debug ("Getting number links...")
    valid_nums = []
    selector_nums = ".number-boxes .number-boxes-item"
    nums = soup.select (selector_nums)
    for num in nums:

        # Ignore premium and private numbers
        classes = num.attrs["class"]
        if "premiumNumber" in classes or "private-number" in classes:
            continue 

        # Get number link
        link = num.select ("a")[0].attrs["href"]
        valid_nums.append (link)

    return valid_nums

def send_message (num):
    """Get all message for the current number, and send to the API"""

    num_formated = num.replace('/sms/', '')

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

        from_sms = str(soup.select (selector_from_sms)[0].getText()).replace("\n", "").replace('"', '').replace("'", "\'").replace('a"', "")
        body_sms = str(soup.select (selector_body_sms)[0].getText()).replace("\n", "").replace('"', '').replace("'", "\'").replace('a"', "")
        date_sms = str(soup.select (selector_date_sms)[0].getText()).replace("\n", "").replace('"', '').replace("'", "\'").replace('a"', "")

        row_data = [num_formated, from_sms, body_sms]

        # Skip duplicates
        query = f"""
                SELECT * 
                FROM `history` 
                WHERE 
                    `body` = "{body_sms}" 
                    and 
                    `from_number` = "{from_sms}" 
                    and 
                    `number` = "{num_formated}";"""
                    
        duplicated = database.run_sql (query)

        if not duplicated:

            # Save row in local
            message = f"Number: {num_formated} | From: {from_sms} | Body: {body_sms} | Date: {date_sms}"
            message_temp = message

            # Generate id
            while True:
                # Generate ID with extra character
                message_temp += "|"
                id_sms = hashlib.md5(message_temp.encode("utf-8")).hexdigest()

                # Validate id
                query = f"""SELECT `id` FROM `history` WHERE id = "{id_sms}";"""
                duplicated_id = database.run_sql (query)

                # End loop
                if not duplicated_id:
                    globals.ids.append(id_sms)
                    break

            # Debug lines
            logger.info (f"{message} | Id: {id_sms}")

            # Save in database
            query = f"INSERT INTO {table} ({id_sms}, {num_formated}, {from_sms}, {body_sms})"
            database.insert_rows (table=table, columns=["id", "number", "from_number", "body"], data=[[id_sms, num_formated, from_sms, body_sms]], nstring=False)

            # Send data to API
            if not debug_mode:

                api_url = f"https://receive-sms.live/receive?sender={from_sms}&msg={body_sms}&msg_id={id_sms}&number={num_formated}&key={api_key}"
                res = requests.get (api_url, headers=headers)
                res.raise_for_status()
            
        else:
            # Skip duplicates
            break

    # Update history file when table extraction ends
    history_obj.update ("history", globals.history) 
    history_obj.update ("ids", globals.ids)    

def main ():
    """Main wrokflow of the program: create thread for extract data
    """

    # Setup pool of threads
    excecutor = ThreadPoolExecutor(max_workers=threads_num)

    # Get numbers
    nums = get_nums ()

    # Run thread for each number
    for num in nums:
        excecutor.submit (send_message, num)

    # Wait to end threads 
    excecutor.shutdown(wait=True)

    # Run program inly once
    if not loop_mode:
        globals.running = False


if __name__ == "__main__":

    # Main loop
    while True:
        if globals.running:
            start_time = time.time()
            main ()      
            
            # Wait time
            if loop_mode:
                end_time = time.time()
                delta_time = end_time - start_time
                if delta_time < wait_time:
                    wait_secs = wait_time - delta_time
                    logger.info (f"Waiting {int(wait_secs)} sec")
                    time.sleep (wait_secs)
                    start_time = time.time()
        else:
            break


    