import os
from datetime import date, datetime
from functools import wraps

import yaml
from cryptography.fernet import Fernet
from flask import g, request
from flask.helpers import make_response
from openapi_core import create_spec
from openapi_core.contrib.flask import FlaskOpenAPIRequest, FlaskOpenAPIResponse
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from yaml import load

from app.config import (
    BASE_PATH,
    ENABLE_OPENAPI_VALIDATION,
    WMONED_FERNET_ENCRYPTION_KEY,
)

openapi_spec = None


def get_openapi_spec():
    global openapi_spec
    if not openapi_spec:
        with open(os.path.join(BASE_PATH, "openapi.yml"), "r") as spec_file:
            spec_dict = load(spec_file, Loader=yaml.Loader)
        openapi_spec = create_spec(spec_dict)

    return openapi_spec


def validate_openapi(function):
    @wraps(function)
    def validate(*args, **kwargs):
        if ENABLE_OPENAPI_VALIDATION:
            spec = get_openapi_spec()
            openapi_request = FlaskOpenAPIRequest(request)
            validator = RequestValidator(spec)
            result = validator.validate(openapi_request)
            result.raise_for_errors()

        response = function(*args, **kwargs)

        if ENABLE_OPENAPI_VALIDATION:
            openapi_response = FlaskOpenAPIResponse(response)
            validator = ResponseValidator(spec)
            result = validator.validate(openapi_request, openapi_response)
            result.raise_for_errors()

        return response

    return validate


def success_response_json(response_content):
    return make_response({"status": "OK", "content": response_content}, 200)


def error_response_json(message: str, code: int = 500):
    return make_response({"status": "ERROR", "message": message}, code)


def to_date(date_input):
    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    if "T" in date_input:
        return datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S").date()

    return datetime.strptime(date_input, "%Y-%m-%d").date()


def to_date_time(date_input):
    if isinstance(date_input, datetime):
        return date_input

    return datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S")


def encrypt(inputUnencrypted: str) -> str:
    f = Fernet(WMONED_FERNET_ENCRYPTION_KEY)
    return f.encrypt(inputUnencrypted.encode()).decode()


def decrypt(inputEncrypted: str) -> tuple:
    f = Fernet(WMONED_FERNET_ENCRYPTION_KEY)
    return f.decrypt(inputEncrypted.encode(), ttl=60 * 60).decode()
