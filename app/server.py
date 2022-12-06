import logging

import sentry_sdk
from flask import Flask, make_response
from requests.exceptions import HTTPError
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import NotFound

import app.zorgned_service as zorgned
from app import auth
from app.config import IS_DEV, SENTRY_DSN, CustomJSONEncoder
from app.helpers import (
    error_response_json,
    success_response_json,
    validate_openapi,
)
from app.crypto import decrypt

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=False
    )


@app.route("/wmoned/voorzieningen", methods=["GET"])
@auth.login_required
@validate_openapi
def get_voorzieningen():
    user = auth.get_current_user()
    voorzieningen = zorgned.get_voorzieningen(user["id"])
    return success_response_json(voorzieningen)


@app.route("/wmoned/document/<string:encrypted_doc_id>", methods=["GET"])
@auth.login_required
@validate_openapi
def get_document(encrypted_doc_id):
    user = auth.get_current_user()
    doc_id = decrypt(encrypted_doc_id)
    document = zorgned.get_document(user["id"], doc_id)
    return success_response_json(document)


@app.route("/status/health")
def health_check():
    return success_response_json("OK")


@app.errorhandler(Exception)
def handle_error(error):

    error_message_original = f"{type(error)}:{str(error)}"

    msg_auth_exception = "Auth error occurred"
    msg_request_http_error = "Request error occurred"
    msg_server_error = "Server error occurred"

    logging.exception(error, extra={"error_message_original": error_message_original})

    if IS_DEV:  # pragma: no cover
        msg_auth_exception = error_message_original
        msg_request_http_error = error_message_original
        msg_server_error = error_message_original

    if isinstance(error, HTTPError):
        return error_response_json(
            msg_request_http_error,
            error.response.status_code,
        )
    elif auth.is_auth_exception(error):
        return error_response_json(msg_auth_exception, 401)

    return error_response_json(msg_server_error, 500)


if __name__ == "__main__":  # pragma: no cover
    app.run()
