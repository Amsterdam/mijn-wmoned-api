from unittest import TestCase

from flask.app import Flask

from app.helpers import error_response_json, success_response_json, to_date


class HelpersTest(TestCase):
    def test_to_date(self):
        d = to_date("2021-04-30")
        self.assertEqual(d.year, 2021)
        self.assertEqual(d.day, 30)
        self.assertEqual(d.month, 4)


app = Flask(__name__)


class RequestHelpersTest(TestCase):
    def test_success_response(self):
        with app.test_request_context():
            resp = success_response_json("dingen")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"content": "dingen", "status": "OK"})

    def test_error_response(self):
        with app.test_request_context():
            resp = error_response_json("Things went south")
            self.assertEqual(resp.status_code, 500)
            self.assertEqual(
                resp.json, {"message": "Things went south", "status": "ERROR"}
            )
