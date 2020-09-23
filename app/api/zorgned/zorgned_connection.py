from urllib.parse import quote

import requests
import json

from .config import credentials, API_URL


class ZorgNedConnection:
    """ This class represents the connection to the ZorgNed API """

    def get_voorzieningen(self, bsn):
        """ Get voorzieningen from ZorgNed based on a BSN """
        res = requests.get(f"{API_URL}/getvoorzieningen?token={quote(credentials['API_KEY'])}&bsn={bsn}")

        return (res.status_code, json.loads(res.text))
