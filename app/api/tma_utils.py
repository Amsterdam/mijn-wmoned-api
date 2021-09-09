import os

from flask_restful import abort
from tma_saml import get_digi_d_bsn


def get_bsn_from_request(request):
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the rquest with the TMA certificate
    try:
        bsn = get_digi_d_bsn(request, tma_certificate)
    except Exception as e:
        abort(400, message=e)
    return bsn


def get_variable(var, default_value=None):
    """Return the environment variable"""
    return os.getenv(var, default_value)


def get_tma_certificate():
    """Get the TMA certificate from a file"""
    tma_cert_location = get_variable("TMA_CERTIFICATE")
    with open(tma_cert_location) as f:
        return f.read()
