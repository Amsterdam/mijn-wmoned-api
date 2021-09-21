from pprint import pprint
from urllib.parse import quote
import logging

import requests
import json

from .config import (
    API_TOKEN_V2,
    credentials,
    API_URL,
    API_URL_V2,
    GEMEENTE_CODE,
    get_mijn_ams_cert_path,
    get_mijn_ams_key_path,
)

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

    def get_voorzieningen_v2(self, bsn):
        """Get voorzieningen from ZorgNed based on a BSN"""
        url = f"{API_URL_V2}/gemeenten/{GEMEENTE_CODE}/ingeschrevenpersonen/{bsn}/aanvragen"

        if log_raw:
            print(f"requesting from: {url}")

        headers = {"Token": API_TOKEN_V2}

        print("\n\n", headers, "\n\n")

        cert = (get_mijn_ams_cert_path(), get_mijn_ams_key_path())

        res = requests.get(url, timeout=9, headers=headers, cert=cert)

        if log_raw:
            print("\n\n", res.text, "\n\n")
            pprint(json.loads(res.text))
            print("Status:", res.status_code)

        return (res.status_code, json.loads(res.text))
