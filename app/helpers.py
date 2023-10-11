import os
from datetime import date, datetime
from functools import wraps
from cryptography.fernet import Fernet

from flask.helpers import make_response


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
