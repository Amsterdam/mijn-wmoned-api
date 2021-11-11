import os


def check_env():
    """
    Checks if all required environment variables have been set
    """
    missing_vars = [v for v in ['WMO_NED_API_KEY', 'WMO_NED_API_URL', 'TMA_CERTIFICATE']
                    if not os.getenv(v, None)]
    if missing_vars:
        raise Exception('Missing environment variables {}'.format(', '.join(missing_vars)))


credentials = dict(
    API_KEY=os.getenv('WMO_NED_API_KEY').strip()
)

SENTRY_DSN = os.getenv('SENTRY_DSN', None)

API_URL = os.getenv('WMO_NED_API_URL').strip()
