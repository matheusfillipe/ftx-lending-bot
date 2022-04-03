"""Simple api wrapper for ftx.com."""

import os
import hmac
import time
import urllib

from requests import Request, Session

API = "https://ftx.com/api/"

# Read API key from environment
KEY = os.environ.get("FTX_KEY")
SECRET = os.environ.get("FTX_SECRET")

if KEY is None or SECRET is None:
    try:
        from conf import KEY, SECRET
    except ModuleNotFoundError:
        raise ValueError("Config file not found. Please create a conf.py file on this same dir defining KEY and SECRET or define the variables: FTX_KEY and FTX_SECRET on your env.")


class Client:
    """Simple rest api request wrapper for ftx.

    This will merelly make post, get, delete requests authed and signed and return the json response.
    Read: https://docs.ftx.com for more info
    """

    def __init__(self):
        """Initialize the client."""
        try:
            from conf import SUBACCOUNT_NAME
        except ImportError:
            self.subaccount_name = None
        else:
            self.subaccount_name = SUBACCOUNT_NAME
        self.session = Session()
        self.session.headers.update({'Accept': 'application/json'})

    def _fix_url(self, url: str) -> str:
        if url.startswith('https://'):
            url = url.replace('https://', '', 1)
        if url.startswith('http://'):
            url = url.replace('http://', '', 1)
        url = "https://" + url.replace("//", "/")
        return url

    def _prepared(self, request: Request) -> None:
        """Prepare and sign the request."""
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(SECRET.encode(), signature_payload, 'sha256').hexdigest()

        prepared.headers['FTX-KEY'] = KEY
        prepared.headers['FTX-SIGN'] = signature
        prepared.headers['FTX-TS'] = str(ts)
        if self.subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self.subaccount_name)
        return prepared

    def get(self, path: str, params: dict = None) -> dict:
        """Perform a get request."""
        url = self._fix_url(API + path)
        request = Request('GET', url, params=params)
        resp = self.session.send(self._prepared(request))
        return resp.json()

    def post(self, path: str, data: dict = None) -> dict:
        """Perform a post request."""
        url = self._fix_url(API + path)
        request = Request('POST', url, json=data)
        resp = self.session.send(self._prepared(request))
        return resp.json()

    def delete(self, path: str, data: dict = None) -> dict:
        """Perform a delete request."""
        url = self._fix_url(API + path)
        request = Request('DELETE', url, json=data)
        resp = self.session.send(self._prepared(request))
        return resp.json()
