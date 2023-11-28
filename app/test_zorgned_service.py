from unittest import TestCase
from unittest.mock import patch

from app import config
from app.test_server import ZorgnedApiMock
from app.zorgned_service import (
    format_aanvraag,
    format_aanvragen,
    get_aanvragen,
    get_voorzieningen,
)

BASE_PATH = config.BASE_PATH


class ZorgnedServiceTest(TestCase):
    @patch("app.zorgned_service.format_aanvragen")
    @patch("app.zorgned_service.requests.post")
    def test_get_aanvragen(self, get_mock, format_mock):
        get_mock.return_value = ZorgnedApiMock(
            {"_embedded": {"aanvraag": [{"foo": "bar"}]}}
        )
        format_mock.return_value = []

        aanvragen = get_aanvragen(123)

        self.assertEqual(aanvragen, [])

        format_mock.assert_called_with([{"foo": "bar"}])

    @patch("app.zorgned_service.requests.post")
    def test_get_aanvragen_fail(self, get_mock):
        get_mock.return_value = ZorgnedApiMock(None)

        with self.assertRaises(TypeError):
            get_aanvragen(123)

    def test_format_aanvraag_partial(self):
        self.maxDiff = None

        source1_formatted = format_aanvraag("2022-01-01", None, None)
        self.assertEqual(source1_formatted, None)

        source2 = {
            "toegewezenProduct": {
                "datumIngangGeldigheid": None,
                "datumEindeGeldigheid": None,
                "actueel": False,
                "leveringsvorm": None,
                "leverancier": {"omschrijving": None},
                "toewijzingen": [],
            }
        }

        with self.assertRaises(KeyError):
            format_aanvraag("2022-01-01", source2, None)

    def test_format_aanvraag_partial2(self):
        source3 = {
            "toegewezenProduct": {
                "datumIngangGeldigheid": None,
                "datumEindeGeldigheid": None,
                "actueel": False,
                "leveringsvorm": None,
                "leverancier": {"omschrijving": None},
                "toewijzingen": [],
            },
            "product": {
                "omschrijving": "een WMO product",
                "productsoortCode": "abc",
            },
        }
        source3_formatted = format_aanvraag("2022-01-01", source3, None)

        self.assertEqual(
            source3_formatted,
            {
                "title": "een WMO product",
                "itemTypeCode": "ABC",
                "dateStart": None,
                "dateEnd": None,
                "isActual": False,
                "deliveryType": "",
                "supplier": None,
                "dateDecision": "2022-01-01",
                "serviceOrderDate": None,
                "serviceDateStart": None,
                "serviceDateEnd": None,
                "documents": None,
            },
        )

    def test_format_aanvraag_complete(self):
        source1 = {
            "product": {
                "productsoortCode": "OVE",
                "omschrijving": "autozitje",
            },
            "toegewezenProduct": {
                "actueel": True,
                "leveringsvorm": "zin",
                "leverancier": {"omschrijving": "Welzorg"},
                "datumIngangGeldigheid": "2014-07-03",
                "datumEindeGeldigheid": "2014-09-03",
                "toewijzingen": [
                    {
                        "datumOpdracht": "2012-12-04",
                        "leverancier": {"omschrijving": "Welzorg"},
                        "leveringen": [
                            {
                                "begindatum": "2014-04-01",
                                "einddatum": "2017-05-31",
                            }
                        ],
                    },
                    {
                        "datumOpdracht": "2017-05-01",
                        "leverancier": {"omschrijving": "Welzorg"},
                        "leveringen": [
                            {
                                "begindatum": "2017-06-01",
                                "einddatum": "2018-02-23",
                            }
                        ],
                    },
                ],
            },
        }

        source1_formatted = format_aanvraag("2012-11-30", source1, None)
        source1_formatted_expected = {
            "title": "autozitje",
            "itemTypeCode": "OVE",
            "dateStart": "2014-07-03",
            "dateEnd": "2014-09-03",
            "isActual": True,
            "deliveryType": "ZIN",
            "supplier": "Welzorg",
            "dateDecision": "2012-11-30",
            "serviceOrderDate": "2017-05-01",
            "serviceDateStart": "2017-06-01",
            "serviceDateEnd": "2018-02-23",
            "documents": None,
        }
        self.assertEqual(source1_formatted, source1_formatted_expected)

    def test_format_aanvraag_complete_2(self):
        source1 = {
            "identificatie": "785401",
            "externe_identificatie": None,
            "product": {
                "identificatie": "12281",
                "productCode": "12281",
                "productsoortCode": "FIE",
                "omschrijving": "rolstoelfiets met hulpmotor",
            },
            "productCategorie": {
                "code": "12",
                "omschrijving": "Vervoervoorzieningen",
            },
            "resultaat": "toegewezen",
            "toegewezenProduct": {
                "datumIngangGeldigheid": "2022-02-11",
                "datumEindeGeldigheid": None,
                "datumCheck": None,
                "actueel": False,
                "omvang": {
                    "volume": 1,
                    "eenheid": {
                        "code": "82",
                        "omschrijving": "Stuks (output)",
                    },
                    "frequentie": {
                        "code": "6",
                        "omschrijving": "Per beschikking",
                    },
                    "omschrijving": "1 stuks (output) per beschikking",
                },
                "leveringsvorm": "zin",
                "leverancier": {
                    "identificatie": "76087055",
                    "agbcode": "76087055",
                    "kvk": None,
                    "omschrijving": "Medipoint",
                },
                "toelichting": None,
                "toewijzingen": [
                    {
                        "toewijzingNummer": "1817681",
                        "toewijzingsDatumTijd": "2022-02-13T22:22:02",
                        "ingangsdatum": "2022-02-11",
                        "einddatum": None,
                        "datumOpdracht": "2022-02-13",
                        "leverancier": {
                            "identificatie": "76087055",
                            "agbcode": "76087055",
                            "kvk": None,
                            "omschrijving": "Medipoint",
                        },
                        "referentieAanbieder": None,
                        "redenWijziging": None,
                        "leveringen": [],
                    }
                ],
            },
        }

        source1_formatted = format_aanvraag("2022-02-13", source1, None)
        source1_formatted_expected = {
            "dateDecision": "2022-02-13",
            "dateEnd": None,
            "dateStart": "2022-02-11",
            "deliveryType": "ZIN",
            "isActual": True,
            "itemTypeCode": "FIE",
            "serviceDateEnd": None,
            "serviceDateStart": None,
            "serviceOrderDate": "2022-02-13",
            "supplier": "Medipoint",
            "title": "rolstoelfiets met hulpmotor",
            "documents": None,
        }
        self.assertEqual(source1_formatted, source1_formatted_expected)

    @patch("app.zorgned_service.encrypt")
    def test_format_aanvragen(self, encrypt_mock):
        id_encrypted_mock = "xx1234567890xx"
        encrypt_mock.return_value = id_encrypted_mock

        source1 = [
            {
                "regeling": {"identificatie": "WMO", "omschrijving": "WMO"},
                "datumAanvraag": "2022-01-02",
                "beschikking": {
                    "datumAfgifte": "2012-11-30",
                    "beschikteProducten": [
                        {
                            "product": {
                                "productsoortCode": "OVE",
                                "omschrijving": "autozitje",
                            },
                            "resultaat": "toegewezen",
                            "toegewezenProduct": {
                                "actueel": True,
                                "leveringsvorm": "zin",
                                "leverancier": {"omschrijving": "Welzorg"},
                                "datumIngangGeldigheid": "2014-07-03",
                                "datumEindeGeldigheid": "2014-09-03",
                                "toewijzingen": [
                                    {
                                        "datumOpdracht": "2012-12-04",
                                        "ingangsdatum": "2014-04-01",
                                        "einddatum": "2017-05-31",
                                        "leverancier": {"omschrijving": "Welzorg"},
                                        "leveringen": [
                                            {
                                                "begindatum": "2014-04-01",
                                                "einddatum": "2017-05-31",
                                            }
                                        ],
                                    },
                                    {
                                        "datumOpdracht": "2017-05-01",
                                        "ingangsdatum": "2017-06-01",
                                        "einddatum": "2018-02-23",
                                        "leverancier": {"omschrijving": "Welzorg"},
                                        "leveringen": [
                                            {
                                                "begindatum": "2017-06-01",
                                                "einddatum": "2018-02-23",
                                            }
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            "product": {
                                "productsoortCode": "OVE",
                                "omschrijving": "ander-dingetje",
                            },
                            "resultaat": "toegewezen",
                            "toegewezenProduct": {
                                "actueel": True,
                                "leveringsvorm": "zin",
                                "leverancier": {"omschrijving": "Anderzorg"},
                                "datumIngangGeldigheid": "2014-07-03",
                                "datumEindeGeldigheid": "2014-09-03",
                                "toewijzingen": [
                                    {
                                        "datumOpdracht": "2012-12-04",
                                        "ingangsdatum": "2014-04-01",
                                        "einddatum": "2017-05-31",
                                        "leverancier": {"omschrijving": "Anderzorg"},
                                        "leveringen": [
                                            {
                                                "begindatum": "2014-04-01",
                                                "einddatum": "2017-05-31",
                                            }
                                        ],
                                    },
                                    {
                                        "datumOpdracht": "2017-05-01",
                                        "ingangsdatum": "2017-06-01",
                                        "einddatum": "2018-02-23",
                                        "leverancier": {"omschrijving": "Anderzorg"},
                                        "leveringen": [
                                            {
                                                "begindatum": "2017-06-01",
                                                "einddatum": "2018-02-23",
                                            }
                                        ],
                                    },
                                ],
                            },
                        },
                    ],
                },
                "documenten": [
                    {
                        "documentidentificatie": "B744593",
                        "omschrijving": "WRV rapport",
                        "datumDefinitief": "2021-03-31T15:28:05",
                        "zaakidentificatie": None,
                    }
                ],
            }
        ]

        source1_formatted = format_aanvragen(source1)

        document = {
            "id": id_encrypted_mock,
            "title": "WRV rapport",
            "url": f"/wmoned/document/{id_encrypted_mock}",
            "datePublished": "2021-03-31T15:28:05",
        }

        aanvraag1 = {
            "title": "autozitje",
            "itemTypeCode": "OVE",
            "dateStart": "2014-07-03",
            "dateEnd": "2014-09-03",
            "isActual": True,
            "deliveryType": "ZIN",
            "supplier": "Welzorg",
            "dateDecision": "2012-11-30",
            "serviceOrderDate": "2017-05-01",
            "serviceDateStart": "2017-06-01",
            "serviceDateEnd": "2018-02-23",
            "documents": None,
        }

        aanvraag2 = {
            "title": "ander-dingetje",
            "itemTypeCode": "OVE",
            "dateStart": "2014-07-03",
            "dateEnd": "2014-09-03",
            "isActual": True,
            "deliveryType": "ZIN",
            "supplier": "Anderzorg",
            "dateDecision": "2012-11-30",
            "serviceOrderDate": "2017-05-01",
            "serviceDateStart": "2017-06-01",
            "serviceDateEnd": "2018-02-23",
            "documents": None,
        }

        self.maxDiff = None

        if config.ZORGNED_DOCUMENT_ATTACHMENTS_ACTIVE:
            aanvraag1["documents"] = [document]
            aanvraag2["documents"] = [document]

        self.assertEqual(len(source1_formatted), 2)
        self.assertEqual(source1_formatted, [aanvraag1, aanvraag2])

    @patch(
        "app.zorgned_service.get_aanvragen",
        side_effect=[
            [
                {"isActual": False, "dateDecision": "2018-01-01"},
            ],
            [
                {
                    "isActual": False,
                    "dateDecision": "2018-01-01",
                    "dateStart": "2018-02-01",
                },
            ],
            [
                {
                    "isActual": True,
                    "dateDecision": "1999-12-31",
                    "serviceDateStart": "2000-02-01",
                },
            ],
            [
                {
                    "isActual": True,
                    "dateDecision": "2017-01-01",
                    "serviceDateStart": None,
                    "dateStart": "2022-02-01",
                },
            ],
        ],
    )
    def test_get_voorzieningen(self, *mocks):
        voorzieningen0 = get_voorzieningen(123)
        self.assertEqual(voorzieningen0, [])

        voorzieningen1 = get_voorzieningen(123)
        self.assertEqual(
            voorzieningen1,
            [
                {
                    "isActual": False,
                    "dateDecision": "2018-01-01",
                    "dateStart": "2018-02-01",
                }
            ],
        )

        voorzieningen2 = get_voorzieningen(123)
        self.assertEqual(voorzieningen2, [])

        voorzieningen3 = get_voorzieningen(123)
        # Does not have serviceDateStart but is considered actual
        self.assertEqual(
            voorzieningen3,
            [
                {
                    "isActual": True,
                    "dateDecision": "2017-01-01",
                    "serviceDateStart": None,
                    "dateStart": "2022-02-01",
                }
            ],
        )
