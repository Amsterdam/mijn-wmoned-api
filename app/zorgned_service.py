from datetime import datetime
import requests
import json
from dpath import util as dpath_util

from app.config import (
    ZORGNED_API_TOKEN,
    ZORGNED_API_URL,
    ZORGNED_GEMEENTE_CODE,
    SERVER_CLIENT_CERT,
    SERVER_CLIENT_KEY,
    logger,
)


def get_title(aanvraag_source):
    beschikteProducten = aanvraag_source.get("beschikking", {}).get(
        "beschikteProducten"
    )
    if beschikteProducten:
        return beschikteProducten[0]["product"]["omschrijving"]


def format_aanvragen(aanvragen_source=[]):
    aanvragen = []

    for aanvraag_source in aanvragen_source:
        product = dpath_util.get(aanvraag_source, "beschikking/beschikteProducten/0")
        toegewezen_product = dpath_util.get(product, "toegewezenProduct")
        print(json.dumps(toegewezen_product, indent=4))
        toewijzing = dpath_util.get(
            toegewezen_product, "toewijzingen", default=[]
        ).pop()
        levering = dpath_util.get(toewijzing, "leveringen", default=[]).pop()

        date_decision = dpath_util.get(toewijzing, "toewijzingsDatumTijd")
        if date_decision:
            date_decision = datetime.strptime(date_decision, "%Y-%m-%dT%H:%M:%S").date()

        aanvraag = {
            # Product
            "title": dpath_util.get(product, "product/omschrijving"),
            "itemTypeCode": dpath_util.get(product, "product/productsoortCode"),
            # Toegewezen product
            "dateStart": dpath_util.get(toegewezen_product, "datumIngangGeldigheid"),
            "dateEnd": dpath_util.get(toegewezen_product, "datumEindeGeldigheid"),
            "isActual": dpath_util.get(toegewezen_product, "actueel", default=False),
            "deliveryType": dpath_util.get(toegewezen_product, "leveringsvorm"),
            "supplier": dpath_util.get(toegewezen_product, "leverancier/omschrijving"),
            # Levering
            "dateDecision": date_decision,
            "serviceOrderDate": dpath_util.get(toewijzing, "datumOpdracht"),
            # Leveringen
            "serviceDateStart": dpath_util.get(levering, "begindatum"),
            "serviceDateEnd": dpath_util.get(levering, "einddatum"),
        }

        print(aanvraag)

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
        if aanvraag["isActual"]:
            voorzieningen.append(aanvraag)

    return voorzieningen
