import logging
import os
import os.path
from datetime import date, time

from flask.json import JSONEncoder

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Sentry configuration.
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT")

# Environment determination
IS_PRODUCTION = SENTRY_ENV == "production"
IS_ACCEPTANCE = SENTRY_ENV == "acceptance"
IS_AP = IS_PRODUCTION or IS_ACCEPTANCE
IS_DEV = os.getenv("FLASK_ENV") == "development" and not IS_AP

# App constants
ENABLE_OPENAPI_VALIDATION = os.getenv("ENABLE_OPENAPI_VALIDATION", not IS_AP)

# ZORGNED specific config
ZORGNED_API_REQUEST_TIMEOUT_SECONDS = 30
ZORGNED_GEMEENTE_CODE = "0363"
ZORGNED_API_TOKEN = os.getenv("WMO_NED_API_TOKEN")
ZORGNED_API_URL = os.getenv("ZORGNED_API_URL")

REGELING_IDENTIFICATIE = "wmo"
BESCHIKT_PRODUCT_RESULTAAT = ["toegewezen"]
DATE_END_NOT_OLDER_THAN = "2018-01-01"
MINIMUM_REQUEST_DATE_FOR_DOCUMENTS = date(2022,1,1)  # After this date documents are WCAG proof.

PRODUCTS_WITH_DELIVERY = {
    "ZIN": [
        "ZIN",
        "WRA",
        "WRA1",
        "WRA2",
        "WRA3",
        "WRA4",
        "WRA5",
        "AAN",
        "AUT",
        "FIE",
        "GBW",
        "OVE",
        "ROL",
        "RWD",
        "RWT",
        "SCO",
        "AO1",
        "AO2",
        "AO3",
        "AO4",
        "AO5",
        "AO6",
        "AO7",
        "AO8",
        "BSW",
        "DBA",
        "DBH",
        "DBL",
        "DBS",
        "KVB",
        "MAO",
        "WMH",
    ],
    "": ["AO2", "AO5", "DBS", "KVB", "WMH", "AAN", "FIE"],
}

# Server security / certificates
SERVER_CLIENT_CERT = os.getenv("MIJN_DATA_CLIENT_CERT")
SERVER_CLIENT_KEY = os.getenv("MIJN_DATA_CLIENT_KEY")

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=LOG_LEVEL,
)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.isoformat(timespec="minutes")
        if isinstance(obj, date):
            return obj.isoformat()

        return JSONEncoder.default(self, obj)
