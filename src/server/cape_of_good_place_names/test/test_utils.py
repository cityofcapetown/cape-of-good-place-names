# coding: utf-8

from __future__ import absolute_import
import base64
import tempfile

from flask import json, current_app

from cape_of_good_place_names import util
from cape_of_good_place_names.test import BaseTestCase, test_geocode_controller


class UtilsTestConfig(object):
    TIMEZONE = "Africa/Johannesburg"


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

    def test_get_geocoders(self):
        """Vanilla test case for get_geocoders

        Utility function for setting up and configuring geocoder objects
        """
        # Setting up config object
        tc = UtilsTestConfig()
        tc.DEFAULT_GEOCODERS = [test_geocode_controller.MockGeocoder]
        current_app.config.from_object(tc)

        # Testing that we get back an instance of the configured geocoder
        gc, *_ = util.get_geocoders()
        self.assertIsInstance(gc, test_geocode_controller.MockGeocoder,
                              "config is not plumbing through to get_geocoders correctly")

        # Checking that the cache is working
        gc2, *_ = util.get_geocoders()
        self.assertIs(gc, gc2, "get_geocoders cache is not working as expected")

        # Flushing the cache and checking we get a new geocoder instance
        gc3, *_ = util.get_geocoders(flush_cache=True)
        self.assertIsNot(gc, gc3, "get_geocoders cache flush is not happening")

    def test_get_secrets(self):
        """Vanilla test case for get_secrets

        Utility function for reading secrets from configured location
        """
        # Setting up config object
        tc = UtilsTestConfig()

        temp_secrets = {"Bob": "your uncle"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file:
            json.dump(temp_secrets, temp_secrets_file)
            temp_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            current_app.config.from_object(tc)

            secrets = util.get_secrets()
            secrets2 = util.get_secrets()
            secrets3 = util.get_secrets(flush_cache=True)

        self.assertDictEqual(secrets, temp_secrets, "get_secrets not reading secrets from configured location")

        # Checking that cache (and its flush) is working as expected
        self.assertIs(secrets, secrets2, "get_secrets cache is not working as expected")
        self.assertIsNot(secrets, secrets3, "get_secrets cache flush is not happening")

        # ToDo test all of the various error paths


if __name__ == '__main__':
    import unittest

    unittest.main()
