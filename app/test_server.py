import json
import os
from unittest.mock import patch

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from app.config import BASE_PATH

MOCK_ENV_VARIABLES = {
    "TMA_CERTIFICATE": __file__,  # any file, it should not be used
    "ZORGNED_API_TOKEN": "123123",
    "ZORGNED_API_URL": "https://some-server",
}

with patch.dict(os.environ, MOCK_ENV_VARIABLES):
    from app.server import app


class ZorgnedApiMock:
    status_code = 200
    response_json = None

    def __init__(self, response_json):
        if isinstance(response_json, str):
            with open(response_json, "r") as read_file:
                self.response_json = json.load(read_file)
        else:
            self.response_json = response_json

    def json(self):
        return self.response_json


class ZorgnedApiMockError:
    status_code = 500

    def json(self):
        return None


class TestAPI(FlaskServerTMATestCase):

    TEST_BSN = "111222333"

    def setUp(self):
        """Setup app for testing"""
        self.client = self.get_tma_test_app(app)
        self.maxDiff = None
        return app

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock(BASE_PATH + "/fixtures/aanvragen.json")
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.get("/api/wmoned/voorzieningen", headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.json["status"], "OK")
        self.assertEqual(
            res.json["content"],
            [
                {
                    "dateDecision": "2012-11-30",
                    "dateEnd": None,
                    "dateStart": "2012-11-30",
                    "deliveryType": "ZIN",
                    "isActual": True,
                    "itemTypeCode": "OVE",
                    "serviceDateEnd": None,
                    "serviceDateStart": "2017-06-01",
                    "serviceOrderDate": "2017-06-01",
                    "supplier": "Welzorg",
                    "title": "autozitje",
                },
                {
                    "dateDecision": "2018-04-25",
                    "dateEnd": None,
                    "dateStart": "2018-04-06",
                    "deliveryType": "ZIN",
                    "isActual": True,
                    "itemTypeCode": "WRA",
                    "serviceDateEnd": None,
                    "serviceDateStart": "2018-05-09",
                    "serviceOrderDate": "2018-04-26",
                    "supplier": "Welzorg",
                    "title": "woonruimteaanpassing",
                },
            ],
        )

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMockError()
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.get("/api/wmoned/voorzieningen", headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 500, res.data)
        self.assertEqual(res.json["status"], "ERROR")
        self.assertTrue("content" not in res.json)

    @patch("app.zorgned_service.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_voorzieningen_saml_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock(None)

        res = self.client.get("/api/wmoned/voorzieningen", headers={})

        self.assertEqual(res.status_code, 400, res.data)
        self.assertEqual(res.json["status"], "ERROR")

    def test_health_page(self):
        res = self.client.get("/status/health")
        self.assertEqual(res.json, "OK")
