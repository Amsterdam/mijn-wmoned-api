import os


def check_env():
    """
    Checks if all required environment variables have been set
    """
    missing_vars = [
        v
        for v in [
            "WMO_NED_API_KEY",
            "WMO_NED_API_URL",
            "TMA_CERTIFICATE",
            "WMO_NED_API_URL_V2",
            "WMO_NED_API_TOKEN",
        ]
        if not os.getenv(v, None)
    ]
    if missing_vars:
        raise Exception(
            "Missing environment variables {}".format(", ".join(missing_vars))
        )


credentials = dict(API_KEY=os.getenv("WMO_NED_API_KEY", "").strip())

SENTRY_DSN = os.getenv("SENTRY_DSN", None)

API_URL = os.getenv("WMO_NED_API_URL", "").strip()


API_URL_V2 = os.getenv("WMO_NED_API_URL_V2", "").strip()
API_TOKEN_V2 = os.getenv("WMO_NED_API_TOKEN", "").strip()
GEMEENTE_CODE = "0363"
