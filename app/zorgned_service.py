import json
import logging

import requests
from dpath import util as dpath_util

from app.config import (
    DATE_DECISION_FROM,
    REGELING_IDENTIFICATIE,
    SERVER_CLIENT_CERT,
    SERVER_CLIENT_KEY,
    ZORGNED_API_TOKEN,
    ZORGNED_API_URL,
    ZORGNED_GEMEENTE_CODE,
)
from app.helpers import to_date


def format_aanvraag(aanvraag_source):

    beschikking = dpath_util.get(aanvraag_source, "beschikking", default=None)

    # TODO: Is this a correct assumption?
    product = dpath_util.get(beschikking, "beschikteProducten/0", default=None)

    if not product:
        logging.info("Product not found %s" % json.dumps(aanvraag_source, indent=4))
        return

    toegewezen_product = dpath_util.get(product, "toegewezenProduct", default=None)
    toewijzing = dpath_util.get(toegewezen_product, "toewijzingen", default=[])

    if toewijzing:
        toewijzing = toewijzing.pop()

    levering = dpath_util.get(toewijzing, "leveringen", default=[])

    if levering:
        levering = levering.pop()

    item_type_code = dpath_util.get(product, "product/productsoortCode")
    if item_type_code:
        item_type_code = item_type_code.upper()

    delivery_type = dpath_util.get(toegewezen_product, "leveringsvorm", default=None)
    if delivery_type:
        delivery_type = delivery_type.upper()

    aanvraag = {
        # Beschikking
        "dateDecision": dpath_util.get(beschikking, "datumAfgifte", default=None),
        # Product
        "title": dpath_util.get(product, "product/omschrijving"),
        "itemTypeCode": item_type_code,
        # Toegewezen product
        "dateStart": dpath_util.get(
            toegewezen_product, "datumIngangGeldigheid", default=None
        ),
        "dateEnd": dpath_util.get(
            toegewezen_product, "datumEindeGeldigheid", default=None
        ),
        "isActual": dpath_util.get(toegewezen_product, "actueel", default=False),
        "deliveryType": delivery_type,
        "supplier": dpath_util.get(
            toegewezen_product, "leverancier/omschrijving", default=None
        ),
        # Levering
        "serviceOrderDate": dpath_util.get(toewijzing, "datumOpdracht", default=None),
        "serviceDateStart": dpath_util.get(levering, "begindatum", default=None),
        "serviceDateEnd": dpath_util.get(levering, "einddatum", default=None),
    }

    return aanvraag


def format_aanvragen(aanvragen_source=[]):
    aanvragen = []

    for aanvraag_source in aanvragen_source:
        regeling_id = dpath_util.get(
            aanvraag_source, "regeling/identificatie", default=None
        )
        if regeling_id == REGELING_IDENTIFICATIE:
            aanvraag_formatted = format_aanvraag(aanvraag_source)
            if aanvraag_formatted:
                aanvragen.append(aanvraag_formatted)

    return aanvragen


def get_aanvragen(bsn):
    url = f"{ZORGNED_API_URL}/gemeenten/{ZORGNED_GEMEENTE_CODE}/ingeschrevenpersonen/{bsn}/aanvragen"

    headers = {"Token": ZORGNED_API_TOKEN}

    cert = (SERVER_CLIENT_CERT, SERVER_CLIENT_KEY)
    res = requests.get(url, timeout=9, headers=headers, cert=cert)

    response_data = res.json()

    logging.debug(json.dumps(response_data, indent=4))

    response_aanvragen = response_data["_embedded"]["aanvraag"]

    return format_aanvragen(response_aanvragen)


def get_voorzieningen(bsn):
    aanvragen = get_aanvragen(bsn)
    voorzieningen = []

    for aanvraag in aanvragen:
        if aanvraag["isActual"] and to_date(aanvraag["dateDecision"]) >= to_date(
            DATE_DECISION_FROM
        ):
            voorzieningen.append(aanvraag)

    return voorzieningen
