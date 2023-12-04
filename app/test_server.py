import json
import os
from unittest.mock import patch

from app.auth import FlaskServerTestCase

MOCK_ENV_VARIABLES = {
    "WMO_NED_API_TOKEN": "123123",
    "ZORGNED_API_URL": "https://some-server",
}

with patch.dict(os.environ, MOCK_ENV_VARIABLES):
    from app import config

    BASE_PATH = config.BASE_PATH
    from app.server import app


class ZorgnedApiMock:
    status_code = 200
    response_json = None

    def __init__(self, response_json=None):
        if isinstance(response_json, str):
            with open(response_json, "r") as read_file:
                self.response_json = json.load(read_file)
        else:
            self.response_json = response_json

    def json(self):
        return self.response_json

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("Request failed")


class ZorgnedApiMockError(ZorgnedApiMock):
    status_code = 500

    def json(self):
        return None


@patch.dict(
    os.environ,
    {
        "MA_BUILD_ID": "999",
        "MA_GIT_SHA": "abcdefghijk",
        "MA_OTAP_ENV": "unittesting",
    },
)
class TestAPI(FlaskServerTestCase):
    app = app
    TEST_BSN = "111222333"

    @patch("app.zorgned_service.requests.post", autospec=True)
    def test_get_voorzieningen(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock(BASE_PATH + "/fixtures/aanvragen.json")

        res = self.get_secure("/wmoned/voorzieningen")

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
                    "documents": None,
                },
                {
                    "dateDecision": "2013-06-17",
                    "dateEnd": None,
                    "dateStart": "2013-02-07",
                    "deliveryType": "ZIN",
                    "isActual": False,
                    "itemTypeCode": "OVE",
                    "serviceDateEnd": "2021-09-27",
                    "serviceDateStart": "2017-06-01",
                    "serviceOrderDate": "2017-06-01",
                    "supplier": "Welzorg",
                    "title": "buggy",
                    "documents": None,
                },
                {
                    "dateDecision": "2015-02-16",
                    "dateEnd": None,
                    "dateStart": "2015-02-16",
                    "deliveryType": "ZIN",
                    "isActual": False,
                    "itemTypeCode": "FIE",
                    "serviceDateEnd": "2021-09-27",
                    "serviceDateStart": "2017-06-01",
                    "serviceOrderDate": "2017-06-01",
                    "supplier": "Welzorg",
                    "title": "driewielfiets 5-9 jr",
                    "documents": None,
                },
                {
                    "dateDecision": "2021-08-26",
                    "dateEnd": None,
                    "dateStart": "2021-08-24",
                    "deliveryType": "ZIN",
                    "isActual": True,
                    "itemTypeCode": "ROL",
                    "serviceDateEnd": None,
                    "serviceDateStart": None,
                    "serviceOrderDate": "2021-08-30",
                    "supplier": "Welzorg",
                    "title": "handbewogen kinderrolstoel",
                    "documents": None,
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
                    "documents": None,
                },
            ],
        )

    @patch("app.zorgned_service.requests.post", autospec=True)
    def test_get_voorzieningen_2(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock(
            BASE_PATH + "/fixtures/aanvragen-2.json"
        )

        res = self.get_secure("/wmoned/voorzieningen")

        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.json["status"], "OK")

    @patch("app.zorgned_service.requests.post", autospec=True)
    def test_get_voorzieningen_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMockError()

        res = self.get_secure("/wmoned/voorzieningen")

        self.assertEqual(res.status_code, 500, res.data)
        self.assertEqual(res.json["status"], "ERROR")
        self.assertTrue("content" not in res.json)

    @patch("app.zorgned_service.requests.post", autospec=True)
    def test_get_voorzieningen_token_error(self, api_mocked):
        api_mocked.return_value = ZorgnedApiMock(None)

        res = self.client.get("/wmoned/voorzieningen")

        self.assertEqual(res.status_code, 401, res.data)
        self.assertEqual(res.json["status"], "ERROR")

    def test_status(self):
        response = self.client.get("/status/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode(),
            '{"content":{"buildId":"999","gitSha":"abcdefghijk","otapEnv":"unittesting"},"status":"OK"}\n',
        )
