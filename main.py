#!/usr/bin/env python3

"""Simple FTX lending bot.

Schedules some tasks.
"""

import datetime
import os
import smtplib
import ssl
import time

import schedule

from lending import (get_balance, last_day_proffit, lend, rate_history,
                     report_status)

# Lets keep a lower minimum than the actual estimative
LOGFILE = 'status.log'
LENDING_RATE_MULTIPLIER = 0.9
LENDING_SIZE_TRHESHOLD = 0.001

# Read configuration from environment
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
MAIL_SENDER = os.environ.get("MAIL_SENDER")
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER")
COINS = [coin.strip() for coin in os.environ.get("COINS", "").split(",")]

if COINS == ['']:
    COINS = ["USDT"]

try:
    from conf import COINS, SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER, SMTP_USER, MAIL_RECEIVER, MAIL_SENDER
except ImportError:
    print("Some variables are missing on the config. Using environment instead!")

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
    for coin in COINS:
        res = lend(coin, get_balance(coin) - LENDING_SIZE_TRHESHOLD, rate_history(coin)['estimate'] * LENDING_RATE_MULTIPLIER)
        print(f"Lend result for {coin}: {res}")

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
    schedule.every().day.at("22:00").do(mail_status)
    schedule.every().day.at("22:00").do(log_status)
    print(f"Starting at {str(datetime.datetime.now())}")
    print(report_status())
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
