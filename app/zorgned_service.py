import base64
import json
import logging
from datetime import date

import dpath
import requests

from app.config import (
    BESCHIKT_PRODUCT_RESULTAAT,
    DATE_END_NOT_OLDER_THAN,
    MINIMUM_REQUEST_DATE_FOR_DOCUMENTS,
    PRODUCTS_WITH_DELIVERY,
    REGELING_IDENTIFICATIE,
    SERVER_CLIENT_CERT,
    SERVER_CLIENT_KEY,
    ZORGNED_API_REQUEST_TIMEOUT_SECONDS,
    ZORGNED_API_TOKEN,
    ZORGNED_API_URL,
    ZORGNED_DOCUMENT_ATTACHMENTS_ACTIVE,
    ZORGNED_GEMEENTE_CODE,
)
from app.helpers import encrypt, to_date


def is_product_with_delivery(aanvraag_formatted):
    delivery_type = aanvraag_formatted.get("deliveryType", "").upper()
    item_type_code = aanvraag_formatted.get("itemTypeCode", "").upper()

    # This check matches the products that should/can/will receive a delivery of goods/service/product (eventually).
    if delivery_type in PRODUCTS_WITH_DELIVERY:
        product_item_type_codes = PRODUCTS_WITH_DELIVERY[delivery_type]
        return item_type_code in product_item_type_codes

    return False


def format_documenten(documenten):
    if not documenten:
        return None

    parsed_documents = []
    for document in documenten:
        id_encrypted = encrypt(document["documentidentificatie"])
        parsed_documents.append(
            {
                "id": id_encrypted,
                "title": dpath.get(document, "omschrijving", None),
                "url": f"/wmoned/document/{id_encrypted}",
                "datePublished": dpath.get(document, "datumDefinitief", None),
            }
        )

    return parsed_documents


def format_aanvraag(date_decision, beschikt_product, documenten):
    if not beschikt_product or not date_decision:
        return None

    toegewezen_product = dpath.get(beschikt_product, "toegewezenProduct", default=None)
    is_actual = dpath.get(toegewezen_product, "actueel", default=False)
    date_end = dpath.get(toegewezen_product, "datumEindeGeldigheid", default=None)

    toewijzingen = dpath.get(toegewezen_product, "toewijzingen", default=[])
    # Take last toewijzing from incoming data
    toewijzing = toewijzingen.pop() if toewijzingen else None

    leveringen = dpath.get(toewijzing, "leveringen", default=[])
    # Take last levering from incoming data
    levering = leveringen.pop() if leveringen else None

    item_type_code = dpath.get(beschikt_product, "product/productsoortCode")
    if item_type_code:
        item_type_code = item_type_code.upper()

    delivery_type = dpath.get(toegewezen_product, "leveringsvorm", default="")
    if delivery_type:
        delivery_type = delivery_type.upper()
    if delivery_type is None:
        delivery_type = ""

    service_date_start = dpath.get(levering, "begindatum", default=None)

    aanvraag = {
        # Beschikking
        "dateDecision": date_decision,
        # Product
        "title": dpath.get(beschikt_product, "product/omschrijving"),
        "itemTypeCode": item_type_code,
        # Toegewezen product
        "dateStart": dpath.get(
            toegewezen_product, "datumIngangGeldigheid", default=None
        ),
        "dateEnd": date_end,
        "isActual": is_actual,
        "deliveryType": delivery_type,
        "supplier": dpath.get(
            toegewezen_product, "leverancier/omschrijving", default=None
        ),
        # Levering
        "serviceOrderDate": dpath.get(toewijzing, "datumOpdracht", default=None),
        "serviceDateStart": service_date_start,
        "serviceDateEnd": dpath.get(levering, "einddatum", default=None),
        "documents": format_documenten(documenten),
    }

    # Voorzieningen without a delivery should be considered actual. The api data returns these items as not-actual.
    # In the front-end we use the isActual boolean to determine if the voorziening is historic or present.
    if (
        is_product_with_delivery(aanvraag)
        and not is_actual
        and not date_end
        and not service_date_start
    ):
        aanvraag["isActual"] = True

    return aanvraag


def format_aanvragen(aanvragen_source=[]):
    aanvragen = []

    for aanvraag_source in aanvragen_source:
        beschikking = dpath.get(aanvraag_source, "beschikking", default=None)
        date_request = dpath.get(aanvraag_source, "datumAanvraag", default=None)
        should_show_documents = (
            to_date(date_request) >= MINIMUM_REQUEST_DATE_FOR_DOCUMENTS
            and ZORGNED_DOCUMENT_ATTACHMENTS_ACTIVE
        )
        date_decision = dpath.get(beschikking, "datumAfgifte", default=None)
        beschikte_producten = dpath.get(beschikking, "beschikteProducten", default=None)
        documenten = []
        if should_show_documents:
            documenten = dpath.get(aanvraag_source, "documenten", default=None)

        if beschikte_producten:
            for beschikt_product in beschikte_producten:
                # Only select products with certain result
                if beschikt_product.get("resultaat") in BESCHIKT_PRODUCT_RESULTAAT:
                    aanvraag_formatted = format_aanvraag(
                        date_decision, beschikt_product, documenten
                    )

                    if aanvraag_formatted:
                        aanvragen.append(aanvraag_formatted)

    return aanvragen


def send_api_request(bsn, operation="", post_message={}):
    headers = None
    cert = None

    headers = {
        "Token": ZORGNED_API_TOKEN,
        "Content-type": "application/json; charset=utf-8",
    }
    cert = (SERVER_CLIENT_CERT, SERVER_CLIENT_KEY)
    url = f"{ZORGNED_API_URL}{operation}"
    default_post_params = {
        "burgerservicenummer": bsn,
        "gemeentecode": ZORGNED_GEMEENTE_CODE,
    }

    res = requests.post(
        url,
        timeout=ZORGNED_API_REQUEST_TIMEOUT_SECONDS,
        headers=headers,
        cert=cert,
        json={**default_post_params, **post_message},
    )

    res.raise_for_status()

    return res


def send_api_request_json(bsn, operation="", post_message={}):
    res = send_api_request(bsn, operation, post_message)

    response_data = res.json()

    logging.debug(json.dumps(response_data, indent=4))

    return response_data


def get_aanvragen(bsn, post_message={}):
    response_data = send_api_request_json(bsn, "/aanvragen", post_message)

    response_aanvragen = response_data["_embedded"]["aanvraag"]

    return format_aanvragen(response_aanvragen)


def has_start_date_in_past(aanvraag_source):
    return (
        aanvraag_source.get("dateStart")
        and to_date(aanvraag_source.get("dateStart")) <= date.today()
    )


def get_voorzieningen(bsn):
    post_message = {
        "maxeinddatum": DATE_END_NOT_OLDER_THAN,
        "regeling": REGELING_IDENTIFICATIE,
    }

    aanvragen = get_aanvragen(bsn, post_message)

    voorzieningen = []

    for aanvraag_source in aanvragen:
        if has_start_date_in_past(aanvraag_source):
            voorzieningen.append(aanvraag_source)

    return voorzieningen


def get_document(bsn, documentidentificatie):
    response_data = send_api_request_json(
        bsn, "/document", {"documentidentificatie": documentidentificatie}
    )

    logging.debug(response_data)

    message_bytes = base64.b64decode(response_data["inhoud"])

    return {
        "Content-Type": response_data["mimetype"],
        "file_data": message_bytes,
    }
