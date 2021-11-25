import json
import logging

import requests
from dpath import util as dpath_util

from app.config import (
    DATE_DECISION_FROM,
    REGELING_IDENTIFICATIE,
    SERVER_CLIENT_CERT,
    SERVER_CLIENT_KEY,
    WMONED_API_URL_V2,
    WMONED_API_KEY,
    WMONED_API_REQUEST_TIMEOUT_SECONDS,
    WMONED_API_TOKEN,
    WMONED_API_URL,
    WMONED_API_V2_ENABLED,
    WMONED_GEMEENTE_CODE,
)
from app.helpers import to_date
from urllib.parse import quote


def format_aanvraag(date_decision, beschikt_product):

    toegewezen_product = dpath_util.get(
        beschikt_product, "toegewezenProduct", default=None
    )
    toewijzing = dpath_util.get(toegewezen_product, "toewijzingen", default=[])

    if toewijzing:
        toewijzing = toewijzing.pop()

    levering = dpath_util.get(toewijzing, "leveringen", default=[])

    if levering:
        levering = levering.pop()

    item_type_code = dpath_util.get(beschikt_product, "product/productsoortCode")
    if item_type_code:
        item_type_code = item_type_code.upper()

    delivery_type = dpath_util.get(toegewezen_product, "leveringsvorm", default=None)
    if delivery_type:
        delivery_type = delivery_type.upper()

    aanvraag = {
        # Beschikking
        "dateDecision": date_decision,
        # Product
        "title": dpath_util.get(beschikt_product, "product/omschrijving"),
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
            beschikking = dpath_util.get(aanvraag_source, "beschikking", default=None)
            date_decision = dpath_util.get(beschikking, "datumAfgifte", default=None)
            beschikte_producten = dpath_util.get(
                beschikking, "beschikteProducten", default=[]
            )

            for beschikt_product in beschikte_producten:
                aanvraag_formatted = format_aanvraag(date_decision, beschikt_product)

                if aanvraag_formatted:
                    aanvragen.append(aanvraag_formatted)

    return aanvragen


def format_aanvragen_v1(aanvragen_source=[]):
    aanvragen = []

    for aanvraag_source in aanvragen_source:
        date_start = aanvraag_source.get("VoorzieningIngangsdatum")
        date_end = aanvraag_source.get("VoorzieningEinddatum")
        date_decision = aanvraag_source.get("Beschikkingsdatum")
        service_order_date = dpath_util.get(
            aanvraag_source, "Levering/Opdrachtdatum", default=None
        )
        service_date_start = dpath_util.get(
            aanvraag_source, "Levering/StartdatumLeverancier", default=None
        )
        service_date_end = dpath_util.get(
            aanvraag_source, "Levering/EinddatumLeverancier", default=None
        )
        aanvraag = {
            "title": aanvraag_source.get("Omschrijving"),
            "itemTypeCode": aanvraag_source.get("Voorzieningsoortcode"),
            "dateStart": to_date(date_start) if date_start else None,
            "dateEnd": to_date(date_end) if date_end else None,
            "isActual": aanvraag_source.get("Actueel"),
            "deliveryType": aanvraag_source.get("Leveringsvorm"),
            "supplier": aanvraag_source.get("Leverancier"),
            "dateDecision": to_date(date_decision) if date_decision else None,
            "serviceOrderDate": to_date(service_order_date)
            if service_order_date
            else None,
            "serviceDateStart": to_date(service_date_start)
            if service_date_start
            else None,
            "serviceDateEnd": to_date(service_date_end) if service_date_end else None,
        }

        aanvragen.append(aanvraag)

    return aanvragen


def get_aanvragen(bsn):

    headers = None
    cert = None

    if WMONED_API_V2_ENABLED:
        headers = {"Token": WMONED_API_TOKEN}
        cert = (SERVER_CLIENT_CERT, SERVER_CLIENT_KEY)
        url = f"{WMONED_API_URL_V2}/gemeenten/{WMONED_GEMEENTE_CODE}/ingeschrevenpersonen/{bsn}/aanvragen"
    else:
        url = (
            f"{WMONED_API_URL}/getvoorzieningen?token={quote(WMONED_API_KEY)}&bsn={bsn}"
        )

    res = requests.get(
        url, timeout=WMONED_API_REQUEST_TIMEOUT_SECONDS, headers=headers, cert=cert
    )

    # Weird use of http status codes in V1 api. The 404 is returned in the case a user doesn't have any content in the remote system.
    if not WMONED_API_V2_ENABLED and res.status_code == 404:
        return []

    response_data = res.json()

    logging.debug(json.dumps(response_data, indent=4))

    if WMONED_API_V2_ENABLED:
        response_aanvragen = response_data["_embedded"]["aanvraag"]
        return format_aanvragen(response_aanvragen)
    else:
        return format_aanvragen_v1(response_data)


def get_voorzieningen(bsn):
    aanvragen = get_aanvragen(bsn)
    voorzieningen = []

    for aanvraag in aanvragen:
        if (
            aanvraag.get("serviceDateStart")
            and aanvraag.get("dateDecision")
            and to_date(aanvraag["dateDecision"]) >= to_date(DATE_DECISION_FROM)
        ):
            voorzieningen.append(aanvraag)

    return voorzieningen
