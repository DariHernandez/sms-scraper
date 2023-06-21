<div><a href='https://github.com/darideveloper/sms-scraper/blob/master/LICENSE' target='_blank'>
            <img src='https://img.shields.io/github/license/darideveloper/sms-scraper.svg?style=for-the-badge' alt='MIT License' height='30px'/>
        </a><a href='https://www.linkedin.com/in/francisco-dari-hernandez-6456b6181/' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=LinkedIn&color=0A66C2&logo=LinkedIn&logoColor=FFFFFF&label=' alt='Linkedin' height='30px'/>
            </a><a href='https://t.me/darideveloper' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=Telegram&color=26A5E4&logo=Telegram&logoColor=FFFFFF&label=' alt='Telegram' height='30px'/>
            </a><a href='https://github.com/darideveloper' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=GitHub&color=181717&logo=GitHub&logoColor=FFFFFF&label=' alt='Github' height='30px'/>
            </a><a href='https://www.fiverr.com/darideveloper?up_rollout=true' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=Fiverr&color=222222&logo=Fiverr&logoColor=1DBF73&label=' alt='Fiverr' height='30px'/>
            </a><a href='https://discord.com/users/992019836811083826' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=Discord&color=5865F2&logo=Discord&logoColor=FFFFFF&label=' alt='Discord' height='30px'/>
            </a><a href='mailto:darideveloper@gmail.com?subject=Hello Dari Developer' target='_blank'>
                <img src='https://img.shields.io/static/v1?style=for-the-badge&message=Gmail&color=EA4335&logo=Gmail&logoColor=FFFFFF&label=' alt='Gmail' height='30px'/>
            </a></div><div align='center'><br><br><img src='https://github.com/darideveloper/sms-scraper/blob/master/logo.png?raw=true' alt='SMS Scraper' height='80px'/>

# SMS Scraper

Get SMS from page: [receive-smss.com](https://receive-smss.com/)

Project type: **client**

</div><br><details>
            <summary>Table of Contents</summary>
            <ol>
<li><a href='#buildwith'>Build With</a></li>
<li><a href='#media'>Media</a></li>
<li><a href='#details'>Details</a></li>
<li><a href='#install'>Install</a></li>
<li><a href='#settings'>Settings</a></li>
<li><a href='#run'>Run</a></li></ol>
        </details><br>

# Build with

<div align='center'><a href='https://requests.readthedocs.io/en/latest/' target='_blank'> <img src='https://requests.readthedocs.io/en/latest/_static/requests-sidebar.png' alt='Requests' title='Requests' height='50px'/> </a><a href='https://www.crummy.com/software/BeautifulSoup/' target='_blank'> <img src='https://github.com/darideveloper/darideveloper/blob/main/imgs/logo%20bs4.png?raw=true' alt='BeautifulSoup4' title='BeautifulSoup4' height='50px'/> </a></div>

# Details

## Workflow

The program get all links / phone numbers from home page, open each phone page with multithreading, extract each received message and send data to the API.

## Multithreading

The program get the number from the home page with a single thread, after it, extract the messages with multithreading. You can configure the number of thread to run at the same time (more details in *Settings* section).

## Duplicated messages

For avoid duplicated, the program use a a data base.
You can create the table with the script: **sql/create_table.sql**

For each row in the SMS table, from each number, the script check if the current message have been saved in the the table, if yes, it means that all the message after the current message, have already been extracted and sent to the API, so the programa skips them an continues with the next table. 

*Note: The first time you run the program, it will take several minutes because it must extract all messages from all numbers. Later the data extraction will be much faster.*

## Proxy

You can use a proxy with login (ip, port, user and password) or without (only ip and port), updating the **config file**

The script only support one proxy at the same time: the best option is use rotative proxies.

# Install

Install all modules from pip: 

``` bash
$ pip install -r requirements.txt
```

# Settings

## config.json
All setting are saved in the **config.json** file. 

```json
{
    "threads_num": 50,
    "debug_mode": false,
    "loop_mode": true,
    "wait_time": 60, 
    "proxy_ip": "64.225.8.192",
    "proxy_port": "80",
    "proxy_user": "sample",
    "proxy_password": "mypas123456",
    "api_key": "p8AQEUBBW**********",
    "dbname": "sms",
    "table": "history",
    "user": "daridev2",
    "password": "alice1999++",
    "hostname": "localhost"
}
```

### threads_num

**Number** of pages (threads) to requests data at the same time.

Try different number for found you best settings. 

*Note: Using a low number will be the program slower, but it will consume less resources. Use a lot of threads will consum more resources, but the program will be faster.* 

### debug_mode

**true** o **false**. 
If *true*, the program extract the data, but dont made any api Call, if *false*, send all data to the api. 

*Note: this variable its usefull for testing (for example, for found the best number of threads). but if you run in any way that hides the terminal (like cron), use this option should be in **false***

### loop_mode

If **true**, run the web scraping in infinity loop. If **false** only run one time and after end the program. 

### wait_time

Minimum of **seconds** to wait after each web scraping loop (only available if *loop_mode* its active).

For sample, if the program takes 40 seconds to extract the new message, and you setup 60 to this variable, the program will wait 20 extra seconds, so that there is at least 60 seconds between each web scraping loop.

If this variable is *0*, the program will skip the wait time.

*Note: this variable is usefull for save resources and avoit web scraping detection.*

### proxy_ip

Ip or host name of the proxy service (optional).

### proxy_port

User for login to the proxy service, if ius required (optional).

### proxy_user

Password for login to the proxy service, if ius required (optional).

### proxy_password

Port of the proxy service (optional).

### api_key

Api key for send datas to the API

### dbname

Name of the databse with the history table

### table

Name of the history table

### user

User name for the database

### password

User password for the database

### hostname

IP / hostname of rthe database (local or remote)

## Clean files

Aditional to the *config.json*, the project use some extra local files to save data. If the files are too big, you should clean the contend keeping the basic structure

### history.json

File where the messages are saved for avoid duplicates. 

*Note: if you clean this file, the next time that you run the program it will requiere more time for extract all messages from all phone (if you are traying to found the best threads number, you should clean this file before each test)*

#### basic structure
If you clean the file, keep the following content:
```json
{
    "history": [],
    "ids": []
}
```

### .log

File for save all debug rows. Usefull for detect errors and see the program flow without terminal (for exaple, when you run the script with cron).

#### basic structure

This files dosent have a requied structure. You can delete all lines.

# Run

For run the program, run the **__ main__.py** file or the **project folder**, with your python 3.10 interpreter.

