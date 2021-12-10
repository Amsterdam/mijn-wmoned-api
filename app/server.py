import json
import logging

import app.zorgned_service as zorgned
import sentry_sdk
from app.config import SENTRY_DSN, CustomJSONEncoder, TMAException
from app.helpers import (
    error_response_json,
    get_tma_user,
    success_response_json,
    validate_openapi,
    verify_tma_user,
)
from flask import Flask, make_response
from requests.exceptions import HTTPError
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=False
    )


@app.route("/wmoned/voorzieningen", methods=["GET"])
@verify_tma_user
@validate_openapi
def get_voorzieningen():
    user = get_tma_user()
    voorzieningen = zorgned.get_voorzieningen(user["id"])
    return success_response_json(voorzieningen)


@app.route("/status/health")
@validate_openapi
def health_check():
    response = make_response(json.dumps("OK"))
    response.headers["Content-type"] = "application/json"
    return response


@app.errorhandler(Exception)
def handle_error(error):
    msg_tma_exception = "TMA error occurred"
    msg_request_http_error = "Request error occurred"
    msg_server_error = "Server error occurred"
    msg_404_error = "Not found"

    logging.exception(error)

    if isinstance(error, NotFound):
        return error_response_json(msg_404_error, 404)
    elif isinstance(error, HTTPError):
        return error_response_json(
            msg_request_http_error,
            error.response.status_code,
        )
    elif isinstance(error, TMAException):
        return error_response_json(msg_tma_exception, 400)

    return error_response_json(msg_server_error, 500)


if __name__ == "__main__":  # pragma: no cover
    app.run()
