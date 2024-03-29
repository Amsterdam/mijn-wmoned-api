import base64
import logging
import os
import os.path
from datetime import date, time
import tempfile

from flask.json.provider import DefaultJSONProvider

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Sentry configuration.
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT")

# Environment determination
IS_PRODUCTION = SENTRY_ENV == "production"
IS_ACCEPTANCE = SENTRY_ENV == "acceptance"
IS_DEV = SENTRY_ENV == "development"
IS_TEST = SENTRY_ENV == "test"

IS_TAP = IS_PRODUCTION or IS_ACCEPTANCE or IS_TEST
IS_AP = IS_ACCEPTANCE or IS_PRODUCTION
IS_OT = IS_DEV or IS_TEST
IS_AZ = os.getenv("IS_AZ", False)

# App constants
VERIFY_JWT_SIGNATURE = os.getenv("VERIFY_JWT_SIGNATURE", IS_AP)

# ZORGNED specific config
ZORGNED_API_REQUEST_TIMEOUT_SECONDS = 30
ZORGNED_GEMEENTE_CODE = "0363"
ZORGNED_API_TOKEN = os.getenv("ZORGNED_API_TOKEN", os.getenv("WMO_NED_API_TOKEN"))
ZORGNED_API_URL = os.getenv("ZORGNED_API_URL")
ZORGNED_DOCUMENT_ATTACHMENTS_ACTIVE = False

WMONED_FERNET_ENCRYPTION_KEY = os.getenv("FERNET_ENCRYPTION_KEY")

REGELING_IDENTIFICATIE = "wmo"
BESCHIKT_PRODUCT_RESULTAAT = ["toegewezen"]
DATE_END_NOT_OLDER_THAN = "2018-01-01"
MINIMUM_REQUEST_DATE_FOR_DOCUMENTS = date(
    2022, 1, 1
)  # After this date documents are WCAG proof.

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

# Server security / certificates for ZorgNed
SERVER_CLIENT_CERT = os.getenv("MIJN_DATA_CLIENT_CERT")
SERVER_CLIENT_KEY = os.getenv("MIJN_DATA_CLIENT_KEY")

# TODO: Add other AZ env conditions after migration.
if IS_AZ and IS_TAP and SERVER_CLIENT_CERT is not None:
    # https://stackoverflow.com/a/46570364/756075
    # Server security / certificates
    cert = tempfile.NamedTemporaryFile(delete=False)
    cert.write(base64.b64decode(SERVER_CLIENT_CERT))
    cert.close()

    key = tempfile.NamedTemporaryFile(delete=False)
    key.write(base64.b64decode(SERVER_CLIENT_KEY))
    key.close()

    SERVER_CLIENT_CERT = cert.name
    SERVER_CLIENT_KEY = key.name

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=LOG_LEVEL,
)


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.isoformat(timespec="minutes")
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)
