import logging
import os
from unittest.mock import patch

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

MOCK_ENV_VARIABLES = {
    "TMA_CERTIFICATE": __file__,  # any file, it should not be used
    "ZORGNED_API_TOKEN": "123123",
    "ZORGNED_API_URL": "https://some-server",
}

with patch.dict(os.environ, MOCK_ENV_VARIABLES):
    from app.config import logger
    from app.server import app


class ZorgnedApiMock:
    status_code = 200

    def json(self):
        return {
            "_embedded": {
                "aanvraag": [
                    {
                        "_links": None,
                        "identificatie": "123123",
                        "regeling": {"identificatie": "WMO", "omschrijving": "WMO"},
                        "datumAanmelding": "2012-11-30",
                        "datumAanvraag": "2012-11-30",
                        "beschikking": {
                            "beschikkingNummer": 123123123,
                            "datumAfgifte": "2012-11-30",
                            "toelichting": "geanonimiseerd",
                            "beschikteProducten": [
                                {
                                    "identificatie": "123123",
                                    "externe_identificatie": None,
                                    "product": {
                                        "identificatie": "12320",
                                        "productCode": "12320",
                                        "productsoortCode": "OVE",
                                        "omschrijving": "autozitje",
                                    },
                                    "productCategorie": {
                                        "code": "12",
                                        "omschrijving": "Vervoervoorzieningen",
                                    },
                                    "resultaat": "toegewezen",
                                    "toegewezenProduct": {
                                        "datumIngangGeldigheid": "2012-11-30",
                                        "datumEindeGeldigheid": None,
                                        "datumCheck": None,
                                        "actueel": True,
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
                                            "identificatie": "LH123123",
                                            "agbcode": None,
                                            "kvk": None,
                                            "omschrijving": "Welzorg",
                                        },
                                        "toelichting": None,
                                        "toewijzingen": [
                                            {
                                                "toewijzingNummer": "123123_OUD",
                                                "toewijzingsDatumTijd": "2012-12-04T00:00:00",
                                                "ingangsdatum": "2012-11-30",
                                                "einddatum": "2017-05-31",
                                                "datumOpdracht": "2012-12-04",
                                                "leverancier": {
                                                    "identificatie": "LH123",
                                                    "agbcode": None,
                                                    "kvk": None,
                                                    "omschrijving": "Welzorg",
                                                },
                                                "referentieAanbieder": None,
                                                "redenWijziging": {
                                                    "code": "01",
                                                    "omschrijving": "Administratieve correctie",
                                                },
                                                "leveringen": [
                                                    {
                                                        "begindatum": "2014-04-01",
                                                        "einddatum": "2017-05-31",
                                                        "redenBeeindiging": {
                                                            "code": "04",
                                                            "omschrijving": "Overplaatsing",
                                                        },
                                                    }
                                                ],
                                            },
                                            {
                                                "toewijzingNummer": "123123",
                                                "toewijzingsDatumTijd": "2017-06-01T00:00:00",
                                                "ingangsdatum": "2012-11-30",
                                                "einddatum": None,
                                                "datumOpdracht": "2017-06-01",
                                                "leverancier": {
                                                    "identificatie": "123123",
                                                    "agbcode": "123123",
                                                    "kvk": None,
                                                    "omschrijving": "Welzorg",
                                                },
                                                "referentieAanbieder": None,
                                                "redenWijziging": None,
                                                "leveringen": [
                                                    {
                                                        "begindatum": "2017-06-01",
                                                        "einddatum": None,
                                                        "redenBeeindiging": None,
                                                    }
                                                ],
                                            },
                                        ],
                                    },
                                }
                            ],
                        },
                        "documenten": [
                            {
                                "documentidentificatie": "B31242",
                                "omschrijving": "Toekenning hulpmiddel zonder keuze (proces 0,1)",
                                "datumDefinitief": "2012-12-04T00:00:00",
                                "zaakidentificatie": None,
                            }
                        ],
                    },
                ]
            }
        }


class ZorgnedApiMockError:
    status_code = 500

    def json(self):
        return None


class TestAPI(FlaskServerTMATestCase):

    TEST_BSN = "111222333"

    def setUp(self):
        """Setup app for testing"""
        self.client = self.get_tma_test_app(app)
        logger.setLevel(logging.DEBUG)
        return app

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock()
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.get("/wmoned/voorzieningen", headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.json["status"], "OK")
        self.assertEqual(
            res.json["content"],
            [
                {
                    "title": "autozitje",
                    "itemTypeCode": "OVE",
                    "dateStart": "2012-11-30",
                    "dateEnd": None,
                    "isActual": True,
                    "deliveryType": "zin",
                    "supplier": "Welzorg",
                    "dateDecision": "2017-06-01",
                    "serviceOrderDate": "2017-06-01",
                    "serviceDateStart": "2017-06-01",
                    "serviceDateEnd": None,
                }
            ],
        )

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMockError()
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.get("/wmoned/voorzieningen", headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 500, res.data)
        self.assertEqual(res.json["status"], "ERROR")
        self.assertTrue("content" not in res.json)

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen_saml_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock()

        res = self.client.get("/wmoned/voorzieningen", headers={})

        self.assertEqual(res.status_code, 400, res.data)
        self.assertEqual(res.json["status"], "ERROR")

    def test_health_page(self):
        res = self.client.get("/status/health")
        self.assertEqual(res.json, "OK")
