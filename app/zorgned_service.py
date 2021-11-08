import requests

from app.config import (
    ZORGNED_API_TOKEN,
    ZORGNED_API_URL,
    ZORGNED_GEMEENTE_CODE,
    SERVER_CLIENT_CERT,
    SERVER_CLIENT_KEY,
    logger,
)


def format_aanvragen(aanvragen_source=[]):
    aanvragen = []

    for aanvraag_source in aanvragen_source:
        aanvraag = {}
        # IS_ACTUAL -> implementeren
        aanvragen.append(aanvraag)

    return aanvragen


def get_aanvragen(bsn):
    url = f"{ZORGNED_API_URL}/gemeenten/{ZORGNED_GEMEENTE_CODE}/ingeschrevenpersonen/{bsn}/aanvragen"

    headers = {"Token": ZORGNED_API_TOKEN}

    cert = (SERVER_CLIENT_CERT, SERVER_CLIENT_KEY)
    res = requests.get(url, timeout=9, headers=headers, cert=cert)

    logger.debug(res)
    response_data = res.json()
    response_aanvragen = response_data["_embedded"]["aanvraag"]

    return format_aanvragen(response_aanvragen)


def get_voorzieningen(bsn):
    aanvragen = get_aanvragen(bsn)
    voorzieningen = []

    for aanvraag in aanvragen:
        if aanvraag["is_actual"]:
            voorzieningen.append(aanvraag)

    return voorzieningen
