import sentry_sdk
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, abort
from flasgger import Swagger
from sentry_sdk.integrations.flask import FlaskIntegration

from .zorgned.config import check_env, SENTRY_DSN
from .zorgned.zorgned_connection import ZorgNedConnection
from .tma_utils import get_bsn_from_request

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        with_locals=True
    )

# Init app and set CORS
app = Flask(__name__)
api = Api(app)
CORS(app=app)

"""
Info about Swagger
==================

In this app we use Flasgger -> https://github.com/rochacbruno/flasgger
Flasgger provides the possibility to describe swagger per endpoint in the
endpoint's description. These description is automatically collected and merged
into a swagger spec which is exposed on '/api/wmo'.
"""


check_env()


# Configure Swagger
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
            "title": "ZorgNed API"
        }
    ],
    "static_url_path": "/api/wmo/static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/api/wmo/"
}
swagger = Swagger(app, config=swagger_config)

# Init connection to ZorgNed
con = ZorgNedConnection()


class Voorzieningen(Resource):
    """ Class representing the '/voorzieningen' endpoint"""

    def get(self):
        """
        Get the voorzieningen based on a BSN
        ---
        parameters:
          - name: BSN
            type: string
            description: The BSN for which the voorzieningen should be fetched
        definitions:
          Voorziening:
            description: Voorziening
            type: object
            properties:
              Omschrijving:
                description: Omschrijving van de voorziening
                type: string
              Wet:
                format: int32
                description: Mogelijke waarden WMO(1), Jeugdwet(2), Overige wetten(3)
                enum: [0, 1, 2, 3]
                type: integer
              Actueel:
                  type: boolean
              Startdatum:
                format: date-time
                description: Ingangsdatum levering indien aanwezig anders ingangsdatum voorziening
                type: string
              Einddatum:
                format: date-time
                description: Einddatum levering indien aanwezig anders einddatum voorziening
                type: string
              Volume:
                format: int32
                description: Volume waarin de voorziening wordt geleverd
                type: integer
              Eenheid:
                description: Eenheid waarin de voorziening wordt geleverd
                enum: ['01', '04', '14', '16', '82', '83']
                type: string
              Frequentie:
                format: int32
                description: Frequentie waarin de voorziening wordt geleverd
                enum: [1, 2, 3, 4, 5, 6]
                type: integer
              Omvang:
                description: Omvang waarin de voorziening wordt geleverd
                type: string
              Leverancier:
                type: string
              Checkdatum:
                format: date-time
                description: Checkdatum van de voorziening
                type: string
              PGBbudget:
                description: PGB informatie
                type: array
                items:
                  - $ref: '#/definitions/PGB'
                example:
                  - jaar: 2017
                    Ingangsdatum: "2018-11-13T15:36:20.727Z"
                    Einddatum: "2018-11-13T15:36:20.727Z"
                    Bedrag: 100.99
          PGB:
            description: PGB informatie van een jaar
            type: object
            properties:
              Jaar:
                format: int32
                description: Jaar van de informatie
                type: integer
              Ingangsdatum:
                format: date-time
                description: Ingangsdatum
                type: string
              Einddatum:
                format: date-time
                description: Einddatum (optioneel)
                type: string
              Bedrag:
                format: double
                description: PGB budget van dat jaar
                type: number
        responses:
          200:
            description: Voorzieningen successfully fetched
            schema:
              $ref: '#/definitions/Voorziening'
          400:
            description: Invalid SAML or BSN
        """
        parser = reqparse.RequestParser()
        token_arg_name = 'x-saml-attribute-token1'
        parser.add_argument(
            token_arg_name,
            location='headers',
            required=True,
            help='SAML token required'
        )
        bsn = get_bsn_from_request(request)
        status, voorzieningen = con.get_voorzieningen(bsn)

        if status == 401:
            # api returns 401 'Token is niet geldig.'
            abort(403, message="Service not available (Invalid token)")
        elif status == 403:
            abort(403, message="Service not available")
        elif status == 404:
            abort(424, message="BSN not found")

        # filter out leverancier for jeugdhulp
        if status == 200:
            for item in voorzieningen:
                if item['Wet'] == 2:
                    del item['Leverancier']

        return voorzieningen


class Health(Resource):
    """ Used in deployment to check if the API lives """

    def get(self):
        return 'OK'


# Add resources to the api
api.add_resource(Voorzieningen, '/api/wmoned/voorzieningen')
api.add_resource(Health, '/status/health')

if __name__ == '__main__':
    app.run()
