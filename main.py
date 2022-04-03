#!/usr/bin/env python3

"""Simple FTX lending bot.

Schedules some tasks.
"""

import datetime
import smtplib
import ssl
import time

import schedule

from lending import (get_balance, last_day_proffit, lend, rate_history,
                     report_status)

# Lets keep a lower minimum than the actual estimative
LOGFILE = 'status.log'
LENDING_RATE_TRHESHOLD = 0.9

try:
    from conf import SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT, MAIL_RECEIVER, MAIL_SENDER
except ModuleNotFoundError:
    raise ValueError("Please create a conf.py file with the following content: SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT, MAIL_RECEIVER, MAIL_SENDER. Set SMTP_USER to None to disable mail sending.")

def status():
    """Print status."""
    balance = get_balance()
    status = ""
    status += f"{str(datetime.datetime.now())}; "
    status += f"Earned: {last_day_proffit()}; "
    status += f"Balance: {', '.join([c + ': ' + str(balance[c]['total']) for c in balance])}\n"
    return status

def renew_lending():
    """Renew lending."""
    print(report_status())
    print("Renewing lending...")
    lend("USDT", get_balance('USDT'), rate_history("USDT")['estimate'] * LENDING_RATE_TRHESHOLD)

def mail_status():
    """Send status report by email."""
    if not SMTP_USER:
        return
    print("Sending status report...")
    context = ssl.create_default_context()

    print("Connecting to SMTP server...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        message = f"""From: My FTX Lending Bot <{MAIL_SENDER}>
To: Myself <{MAIL_RECEIVER}>
MIME-Version: 1.0
Content-type: text/html
Subject: FTX Bot report {str(datetime.datetime.now()).split()[0]}


<h2>This is your report for today</h2>
<br>
<pre>{report_status()}</pre>"""
        server.sendmail(MAIL_SENDER, MAIL_RECEIVER, message)
        print("Mail sent")


def log_status():
    """Save status to file."""
    print("Saving status...")
    with open(LOGFILE, 'a') as f:
        f.write(status())

def main():
    schedule.every().hour.at("50:30").do(renew_lending)
    schedule.every().day.at("12:00").do(mail_status)
    schedule.every().day.at("12:00").do(log_status)
    print("Starting...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
