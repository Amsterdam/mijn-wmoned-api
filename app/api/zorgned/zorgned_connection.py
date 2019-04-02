from urllib.parse import urlencode

import requests
import json

from .config import credentials, API_URL


class ZorgNedConnection:
    """ This class represents the connection to the ZorgNed API """

    def get_voorzieningen(self, bsn):
        """ Get voorzieningen from ZorgNed based on a BSN """
        params = urlencode({
            "token": credentials['API_KEY'],
            "bsn": bsn
        })
        res = requests.get('{}/getvoorzieningen?{}'.format(API_URL, params))

        return (res.status_code, json.loads(res.text))
