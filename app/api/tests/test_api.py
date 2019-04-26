import os
from unittest.mock import patch, ANY
from tma_saml import FlaskServerTMATestCase

# prepare environment for testing
os.environ['WMO_NED_API_KEY'] = "invalid key"
os.environ['WMO_NED_API_URL'] = "invalid url"
os.environ['TMA_CERTIFICATE'] = __file__  # any file, it should not be used


from ..server import app  # noqa: E402

ZorgNedConnectionLocation = 'api.zorgned.zorgned_connection.ZorgNedConnection'


def get_expected_data(*args):
    return (200,
            [
                {
                    "Omschrijving": "driewielfiets 5-9 jr",
                    "Wet": 1,
                    "Actueel": False,
                    "Startdatum": "2015-02-16T00:00:00",
                    "Einddatum": "2017-05-31T00:00:00",
                    "Volume": 1,
                    "Eenheid": "82",
                    "Frequentie": 6,
                    "Leveringsvorm": "ZIN",
                    "Omvang": "1 stuks per beschikking",
                    "Leverancier": "Welzorg",
                    "Checkdatum": None,
                    "PGBbudget": []
                },
                {
                    "Omschrijving": "Specialistische jeugdhulp",
                    "Wet": 2,
                    "Actueel": False,
                    "Startdatum": "2016-06-07T00:00:00",
                    "Einddatum": "2017-06-07T00:00:00",
                    "Volume": 9999,
                    "Eenheid": "04",
                    "Frequentie": 4,
                    "Leveringsvorm": "ZIN",
                    "Omvang": "9999 uren per maand",
                    "Leverancier": "Cordaan",
                    "Checkdatum": None,
                    "PGBbudget": []
                },
            ])


class TestAPI(FlaskServerTMATestCase):

    TEST_BSN = '111222333'
    VOORZIENINGEN_URL = '/api/wmoned/voorzieningen'

    def setUp(self):
        """ Setup app for testing """
        self.client = self.get_tma_test_app(app)
        return app

    # =====================
    # Test the /wmo/voorzieningen endpoint
    # =====================

    @patch(ZorgNedConnectionLocation + '.get_voorzieningen', autospec=True)
    @patch('api.server.get_bsn_from_request', lambda x: '111222333')
    def test_get_voorzieningen(self, mocked_method):
        """
        Test if getting is allowed, if the SAML token is correctly decoded and
        if the ZorgNedConnection is called
        """
        # Mock the ZOrgNedConnection response
        mocked_method.return_value = get_expected_data()

        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call thr SPI with SAML headers
        res = self.client.get(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        # Check if the mocked method got called with the expected args
        # ANY covers the self argument
        mocked_method.assert_called_once_with(ANY, self.TEST_BSN)

    @patch(ZorgNedConnectionLocation + '.get_voorzieningen', side_effect=get_expected_data)
    @patch('api.server.get_bsn_from_request', lambda x: '111222333')
    def test_get_voorzieningen_jeughulp_filtered(self, mock_get_voorzieningen):
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call thr SPI with SAML headers
        res = self.client.get(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 200)

        data = res.json
        # make sure wet 1 has the Leverancier
        self.assertEqual(data[0]['Wet'], 1)
        self.assertTrue(data[0].get('Leverancier', False))

        # make sure wet 2 (jeugdhulp) does not have Leverancier
        self.assertEqual(data[1]['Wet'], 2)
        self.assertFalse(data[1].get('Leverancier', False))

    def test_get_voorzieningen_invalid_saml(self):
        """ Test if an invalid SAML token gets rejected """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        saml_key = None
        invalid_saml_value = None
        # Invalidate the SAML token
        for k, v in SAML_HEADERS.items():
            saml_key = k
            invalid_saml_value = bytes(str(v)[:-7] + 'malware', 'utf-8')

        SAML_HEADERS[saml_key] = invalid_saml_value

        # Call the API with SAML headers
        res = self.client.get(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)

    def test_get_voorzieningen_invalid_bsn(self):
        """ Test if an invalid SAML token get rejected """
        # Create SAML headers with a BSN which doesn't meet the elf proef
        SAML_HEADERS = self.add_digi_d_headers('123456789')

        # Call the API with SAML headers
        res = self.client.get(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)

    def test_update_voorzieningen(self):
        """ Test if updating is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.put(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)
        res = self.client.patch(self.VOORZIENINGEN_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

    def test_post_voorzieningen(self):
        """ Test if posting is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.post(
            self.VOORZIENINGEN_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

    def test_delete_voorzieningen(self):
        """ Test if deleting is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.delete(
            self.VOORZIENINGEN_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

        # ============================
        # Test miscellaneous endpoints
        # ============================

        def test_health_page(self):
            """ Test if the health page lives """
            res = self.client.get('/status/health')
            self.assertEqual(res.json, 'OK')

        def test_swagger(self):
            """ Test if swagger lives """
            res = self.client.get('/api/wmo')
            self.assertEqual(res.status_code, 200)
