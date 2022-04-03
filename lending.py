"""Lending data and proffit calculations."""
import datetime

from client import Client

client = Client()

def get_balance(coin: str = None) -> float:
    """Return the balance of a coin.

    If no coin is specified, return the balance for all coins with a
    greater than 0 total.
    """
    all_coins = {}
    for _coin in client.get("/wallet/balances")['result']:
        if coin is None and float(_coin['total']) > 0:
            all_coins[_coin['coin']] = _coin
        if _coin['coin'] == coin:
            return _coin['total']
    return all_coins

def from_start_to_end(start, end) -> dict:
    """Return the lending data from start to end."""
    start_time = start.strftime('%s')
    end_time = end.strftime('%s')
    resp = client.get('spot_margin/lending_history', params={"start_time": start_time, "end_time": end_time})
    return resp

def last_day_proffit() -> float:
    """Return the last 24 hours of lending data."""
    today = datetime.datetime.utcnow()
    yesterday = today - datetime.timedelta(days=1)
    return sum([d['proceeds'] for d in from_start_to_end(yesterday, today)['result']])

def last_week_proffit() -> float:
    """Return the last 7 days of lending data."""
    today = datetime.datetime.utcnow()
    week_ago = today - datetime.timedelta(days=7)
    return sum([d['proceeds'] for d in from_start_to_end(week_ago, today)['result']])

def last_month_proffit() -> float:
    """Return the last 30 days of lending data."""
    today = datetime.datetime.utcnow()
    month_ago = today - datetime.timedelta(days=30)
    return sum([d['proceeds'] for d in from_start_to_end(month_ago, today)['result']])

def rate_history(coin: str) -> dict:
    """Return the lending rate history for coin."""
    resp = client.get("/spot_margin/lending_rates")
    for _coin in resp['result']:
        if _coin['coin'] == coin:
            return _coin

def lend(coin: str, ammount: float, apy: float) -> dict:
    """Lend ammount of coin."""
    return client.post('/spot_margin/offers', {"coin": coin, "size": ammount, "rate": apy})

def report_status() -> str:
    """General Wallet info."""
    status = ""
    balance = get_balance()
    status += "------------------------------------------------------------\n"
    status += f"---------{str(datetime.datetime.now())}-------------------------\n"
    status += f"Earned: {last_month_proffit()} USD in the last 30 days\n"
    status += f"Earned: {last_week_proffit()} USD in the last 7 days\n"
    status += f"Earned: {last_day_proffit()} USD in the last 24 hours\n"
    status += f"Balance: {', '.join([c + ': ' + str(balance[c]['total']) for c in balance])}\n"
    return status

if __name__ == "__main__":
    print(report_status())
