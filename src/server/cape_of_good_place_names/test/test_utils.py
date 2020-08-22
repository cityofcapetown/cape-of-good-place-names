# coding: utf-8

from __future__ import absolute_import
import base64
import random
import tempfile

from flask import json, current_app

from cape_of_good_place_names import util
from cape_of_good_place_names.config import config
from cape_of_good_place_names.test import BaseTestCase, test_geocode_controller


class UtilsTestConfig(object):
    TIMEZONE = "Africa/Johannesburg"
    DEFAULT_GEOCODERS = []
    CONFIGURABLE_GEOCODERS = []


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

        random.seed(1234)
        self.test_secret_key = "Bob"
        self.test_secret_value = "your uncle"
        self.test_secrets = {self.test_secret_key: self.test_secret_value}

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

    def test_configurable_geocoders(self):
        """Testing get_geocoders sets up a configurable geocoder correctly

        Configurable geocoders are geocoders that need additonal config (e.g. secrets)
        """
        # Setting up config object
        tc = UtilsTestConfig()

        random_value = random.random()
        tc.SOME_RANDOM_VALUE = random_value
        tc.DEFAULT_GEOCODERS = []
        tc.CONFIGURABLE_GEOCODERS = [
            (
                test_geocode_controller.MockGeocoder, {
                    "proxy_url": [config.ConfigNamespace.CONFIG, "SOME_RANDOM_VALUE"]
                }
            ),
            (
                test_geocode_controller.MockGeocoder, {
                    "proxy_url": [config.ConfigNamespace.SECRETS, self.test_secret_key]
                }
            ),
            (
                test_geocode_controller.MockGeocoder, {
                    "proxy_url": [config.ConfigNamespace.CONFIG, "SOME_OTHER_RANDOM_VALUE"]
                }
            )
        ]

        # Setting secrets values
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            temp_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name

            # Actually configuring the app
            current_app.config.from_object(tc)

            # Testing the configuration from config namespace works
            gc, *_ = util.get_geocoders(flush_cache=True)
            self.assertIsInstance(gc, test_geocode_controller.MockGeocoder,
                                  "Configurable geocoder using config namespace not being returned")
            self.assertEqual(gc.proxy_url, random_value,
                             "Configurable geocoder using config namespace not being configured correctly")

            _, gc2, *_ = util.get_geocoders()
            self.assertIsInstance(gc, test_geocode_controller.MockGeocoder,
                                  "Configurable geocoder using secrets namespace not being returned")
            self.assertEqual(gc2.proxy_url, self.test_secret_value,
                             "Configurable geocoder using secrets namespace not being configured correctly")

            self.assertEqual(len(util.get_geocoders(flush_cache=True)), 2, "Wrong number of geocoders being returned")

    def test_get_secrets(self):
        """Vanilla test case for get_secrets

        Utility function for reading secrets from configured location
        """
        # Setting up config object
        tc = UtilsTestConfig()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            temp_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            current_app.config.from_object(tc)

            secrets = util.get_secrets()
            secrets2 = util.get_secrets()
            secrets3 = util.get_secrets(flush_cache=True)

        self.assertDictEqual(secrets, self.test_secrets, "get_secrets not reading secrets from configured location")

        # Checking that cache (and its flush) is working as expected
        self.assertIs(secrets, secrets2, "get_secrets cache is not working as expected")
        self.assertIsNot(secrets, secrets3, "get_secrets cache flush is not happening")

        # ToDo test all of the various error paths


if __name__ == '__main__':
    import unittest

    unittest.main()
