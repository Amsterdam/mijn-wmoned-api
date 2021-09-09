from pprint import pprint
from urllib.parse import quote
import logging

import requests
import json

from .config import credentials, API_URL

logger = logging.getLogger(__name__)

log_raw = False


class ZorgNedConnection:
    """This class represents the connection to the ZorgNed API"""

    def get_voorzieningen(self, bsn):
        """Get voorzieningen from ZorgNed based on a BSN"""
        url = f"{API_URL}/getvoorzieningen?token={quote(credentials['API_KEY'])}&bsn={bsn}"
        if log_raw:
            print(f"requesting from: {url}")

        res = requests.get(url, timeout=9)

        if log_raw:
            print("\n\n", res.text, "\n\n")
            pprint(json.loads(res.text))
            print("Status:", res.status_code)

        return (res.status_code, json.loads(res.text))
