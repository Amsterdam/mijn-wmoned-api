from unittest import TestCase

from unittest.mock import patch
from app.test_server import ZorgnedApiMock

from app.zorgned_service import (
    format_aanvraag,
    format_aanvragen,
    get_aanvragen,
    get_voorzieningen,
)


class ZorgnedServiceTest(TestCase):
    @patch("app.zorgned_service.format_aanvragen")
    @patch("app.zorgned_service.requests.get")
    def test_get_aanvragen(self, get_mock, format_mock):
        get_mock.return_value = ZorgnedApiMock(
            {"_embedded": {"aanvraag": [{"foo": "bar"}]}}
        )
        format_mock.return_value = []

        aanvragen = get_aanvragen(123)

        self.assertEqual(aanvragen, [])

        format_mock.assert_called_with([{"foo": "bar"}])

    @patch("app.zorgned_service.requests.get")
    def test_get_aanvragen_fail(self, get_mock):
        get_mock.return_value = ZorgnedApiMock(None)

        with self.assertRaises(TypeError):
            get_aanvragen(123)

    def format_aanvraag_partial(self):

        self.maxDiff = None

        source1 = {"beschikking": {"beschikteProducten": []}}
        source1_formatted = format_aanvraag(source1)
        self.assertEqual(source1_formatted, None)

        source2 = {
            "beschikking": {
                "beschikteProducten": [
                    {
                        "toegewezenProduct": {
                            "datumIngangGeldigheid": None,
                            "datumEindeGeldigheid": None,
                            "actueel": False,
                            "leveringsvorm": None,
                            "leverancier": {"omschrijving": None},
                            "toewijzingen": [],
                        }
                    }
                ]
            }
        }

        with self.assertRaises(KeyError):
            format_aanvraag(source2)

        source3 = source2
        source3["beschikking"]["beschikteProducten"][0]["product"] = {
            "omschrijving": "een WMO product",
            "productsoortCode": "abc",
        }
        source3_formatted = format_aanvraag(source3)

        self.assertEqual(
            source3_formatted,
            {
                "title": "een WMO product",
                "itemTypeCode": "ABC",
                "dateStart": None,
                "dateEnd": None,
                "isActual": False,
                "deliveryType": None,
                "supplier": None,
                "dateDecision": None,
                "serviceOrderDate": None,
                "serviceDateStart": None,
                "serviceDateEnd": None,
            },
        )

    def format_aanvraag_complete(self):
        source1 = {
            "beschikking": {
                "datumAfgifte": "2012-11-30",
                "beschikteProducten": [
                    {
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
                ],
            },
            "documenten": [],
        }

        source1_formatted = format_aanvraag(source1)
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
        }
        self.assertEqual(source1_formatted, source1_formatted_expected)

    @patch("app.zorgned_service.format_aanvraag")
    def test_format_aanvragen(self, format_aanvraag_mock):

        aanvraag = {"title": "Foo", "itemTypeCode": "BAR"}

        format_aanvraag_mock.return_value = aanvraag

        source1 = [
            {
                "regeling": {"identificatie": "WMO", "omschrijving": "WMO"},
            },
            {
                "regeling": {"identificatie": "BLAP", "omschrijving": "WMO"},
            },
            {
                "regeling": {"identificatie": "WMO", "omschrijving": "WMO"},
            },
        ]

        source1_formatted = format_aanvragen(source1)

        self.assertEqual(len(source1_formatted), 2)
        self.assertEqual(source1_formatted, [aanvraag, aanvraag])

    @patch(
        "app.zorgned_service.get_aanvragen",
        side_effect=[
            [
                {"isActual": False, "dateDecision": "2018-01-01"},
            ],
            [
                {"isActual": True, "dateDecision": "2016-12-31"},
            ],
            [
                {"isActual": True, "dateDecision": "2017-01-01"},
            ],
        ],
    )
    def test_get_voorzieningen(self, *mocks):

        voorzieningen1 = get_voorzieningen(123)
        self.assertEqual(voorzieningen1, [])

        voorzieningen2 = get_voorzieningen(123)
        self.assertEqual(voorzieningen2, [])

        voorzieningen3 = get_voorzieningen(123)
        self.assertEqual(
            voorzieningen3, [{"isActual": True, "dateDecision": "2017-01-01"}]
        )
