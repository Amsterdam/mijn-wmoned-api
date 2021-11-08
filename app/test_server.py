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
        return {"_embedded": {"aanvraag": []}}


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
        self.assertEqual(res.json["content"], [])

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
