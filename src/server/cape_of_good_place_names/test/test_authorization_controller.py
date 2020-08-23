# coding: utf-8

from __future__ import absolute_import
import base64
import tempfile

from flask import json, current_app
from geocode_array.Geocoder import Geocoder
from six import BytesIO

from cape_of_good_place_names import util
from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class AuthorizationTestConfig(object):
    TIMEZONE = "Africa/Johannesburg"
    GEOCODERS = []
    SCRUBBERS = []
    USER_SECRETS_FILE = ""
    USER_SECRETS_SALT_KEY = ""


class TestAuthorizationController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        self.test_secret_key = "Bob"
        self.test_secret_value = "your uncle"
        self.test_secrets = {self.test_secret_key: self.test_secret_value}

        self.test_user_secrets = {
            '3d224707797b570fe4523f6ff4b9d68be72815d80c19530000919efad9e6cfe2':  # sha256("Bob" + "your uncle")
                '037525e1e2b6f9f169c483caf4aba43bc50885fdb9a2efe023635cd9534999ab'
            # sha256("your uncle" + "your uncle")
        }

        cred_string = f"{self.test_secret_key}:{self.test_secret_value}"
        credentials = base64.b64encode(cred_string.encode('utf-8')).decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}
        current_app.logger.debug(f"self.authorisation_headers={self.authorisation_headers}")

        current_app.config.from_object(AuthorizationTestConfig)
        util.flush_caches()

    def test_insecure_auth(self):
        """Tests for auth

        Service should allow anyone to call, provided there is a basic auth header
        """
        query_string = [('address', 'address_example')]
        # Testing the happy case
        response = self.client.open(
            '/v1/scrub',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Testing the unhappy case (no creds)
        response2 = self.client.open(
            '/v1/scrub',
            method='GET',
            query_string=query_string,
        )
        self.assert401(response2,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_secure_auth(self):
        """Tests for auth in secure mode

        Service should only allow valid usernames to call
        """
        # Setting up config object
        tc = AuthorizationTestConfig()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file, \
                tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_user_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            json.dump(self.test_user_secrets, temp_user_secrets_file)
            temp_secrets_file.flush()
            temp_user_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            tc.USER_SECRETS_FILE = temp_user_secrets_file.name
            tc.USER_SECRETS_SALT_KEY = self.test_secret_key

            current_app.config.from_object(tc)
            util.flush_caches()

            current_app.logger.info(f"**Happy Case Test**")
            query_string = [('address', 'address_example')]
            # Testing the happy case
            response = self.client.open(
                '/v1/scrub',
                method='GET',
                query_string=query_string,
                headers=self.authorisation_headers
            )
            self.assert200(response,
                           'Response body is : ' + response.data.decode('utf-8'))

            # Testing the unhappy case (no creds)
            current_app.logger.info(f"**Unhappy Case Test**")
            response2 = self.client.open(
                '/v1/scrub',
                method='GET',
                query_string=query_string,
            )
            self.assert401(response2,
                           'Response body is : ' + response2.data.decode('utf-8'))

            # Testing the unhappy case (bad creds)
            current_app.logger.info(f"**Unhappy Case Test 2**")
            credentials = base64.b64encode(b"Fanny:your aunt").decode('utf-8')
            authorisation_headers2 = {"Authorization": "Basic {}".format(credentials)}

            response3 = self.client.open(
                '/v1/scrub',
                method='GET',
                query_string=query_string,
                headers=authorisation_headers2
            )
            self.assert401(response3,
                           'Response body is : ' + response3.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
