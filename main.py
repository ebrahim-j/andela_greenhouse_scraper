import os
import datetime
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import requests
from bs4 import BeautifulSoup

def send_email(openings_list):
    openings = ""
    for i in openings_list:
        openings += '<li><a href="{}">{}</a></li>'.format(i[1], i[0])
    html = '<strong>Following was found on greenhouse today as at {}:</br><ul>{}</ul></strong>'.format(datetime.datetime.now(), openings)
    message = Mail(
            from_email='info@fakhrifarm.com',
            to_emails='ebzjanoo@gmail.com',
            subject='OPENINGS ON GREENHOUSE',
            html_content=html)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def run():
    URL = 'https://boards.greenhouse.io/partnerengagementstaffing'
    page = requests.get(URL)
    openings_list = []

    watchlist = ["python", "flask", "springboot", "spring-boot", "spring boot", "django"]

    soup = BeautifulSoup(page.content, 'html.parser')

    openings = soup.find_all('div', attrs={'class': 'opening'})

    for opening in openings:
        name = opening.a.get_text()
        if ("se" in name.lower()) and (any(i in name.lower() for i in watchlist)):
            link = 'https://boards.greenhouse.io' + opening.a['href']
            openings_list.append((name, link))

    if len(openings_list) > 0:
        send_email(openings_list)

sched = BlockingScheduler()

# @sched.scheduled_job('interval', hours=10)
@sched.scheduled_job('interval', seconds=10)
def timed_job():
    run()

sched.start()
