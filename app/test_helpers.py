from unittest import TestCase

from unittest.mock import MagicMock, patch

from flask.app import Flask
from flask import json, request
from flask.wrappers import Response
from openapi_core.spec.shortcuts import create_spec
from yaml import load
import yaml
from app.helpers import (
    error_response_json,
    success_response_json,
    to_date,
    validate_openapi,
)
from openapi_core.exceptions import MissingRequiredParameter
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue


class HelpersTest(TestCase):
    def test_to_date(self):
        d = to_date("2021-04-30")
        self.assertEqual(d.year, 2021)
        self.assertEqual(d.day, 30)
        self.assertEqual(d.month, 4)


app = Flask(__name__)

test_spec = """
openapi: 3.0.3
info:
  title: WMO Test spec
  version: 0.0.1
paths:
  /test:
    parameters:
      - name: x-saml-attribute-token1
        in: header
        description: TMA encoded BSN
        required: true
        schema:
          type: string
    get:
      summary: returns "OK"
      responses:
        '200':
          description: Returns "OK"
          content:
            application/json:
              schema:
                type: string
                enum:
                  - 'OK'
"""

test_spec = create_spec(load(test_spec, Loader=yaml.Loader))


def create_mock_dummy(content):

    dummy = MagicMock(
        return_value=Response(
            status=200,
            mimetype="application/json",
            response=json.dumps(content),
        )
    )

    @validate_openapi
    def route_handler():
        return dummy()

    return (route_handler, dummy)


class RequestHelpersTest(TestCase):
    @patch("app.helpers.get_openapi_spec")
    def test_validate_ok(self, open_api_spec_mock):

        open_api_spec_mock.return_value = test_spec

        with app.test_request_context(
            "/test", headers={"x-saml-attribute-token1": "saml-token"}
        ):

            (route_ok, dummy_ok) = create_mock_dummy("OK")
            route_ok()
            dummy_ok.assert_called_once()

    @patch("app.helpers.get_openapi_spec")
    def test_validate_nok(self, open_api_spec_mock):

        open_api_spec_mock.return_value = test_spec

        with app.test_request_context(
            "/test", headers={"x-saml-attribute-token1": "saml-token"}
        ):
            (route_nok, dummy_nok) = create_mock_dummy("NOK")
            with self.assertRaises(InvalidSchemaValue):
                route_nok()

    @patch("app.helpers.get_openapi_spec")
    def test_validate_request_not_ok(self, open_api_spec_mock):

        open_api_spec_mock.return_value = test_spec

        with app.test_request_context("/test"):
            (route_ok, dummy_ok) = create_mock_dummy("OK")
            with self.assertRaises(MissingRequiredParameter):
                route_ok()
            dummy_ok.assert_not_called()

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
