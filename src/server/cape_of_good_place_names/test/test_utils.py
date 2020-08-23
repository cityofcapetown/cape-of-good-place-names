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
    GEOCODERS = []
    SCRUBBERS = []
    USER_SECRETS_FILE = ""
    USER_SECRETS_SALT_KEY = ""


class TestUtils(BaseTestCase):
    """Unit test for utils module"""

    def setUp(self) -> None:
        random.seed(1234)
        self.test_secret_key = "Bob"
        self.test_secret_value = "your uncle"
        self.test_secrets = {self.test_secret_key: self.test_secret_value}

        self.test_user_secrets = {
            '3d224707797b570fe4523f6ff4b9d68be72815d80c19530000919efad9e6cfe2':  # sha256("Bob" + "your uncle")
                '037525e1e2b6f9f169c483caf4aba43bc50885fdb9a2efe023635cd9534999ab'  # sha256("your uncle" + "your uncle")
        }

    def test_get_geocoders(self):
        """Vanilla test case for get_geocoders

        Utility function for setting up and configuring geocoder objects
        """
        # Setting up config object
        tc = UtilsTestConfig()
        tc.GEOCODERS = (
            (test_geocode_controller.MockGeocoder, {}),
        )
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
        tc.GEOCODERS = (
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
        )

        # Setting secrets values
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            temp_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            tc.USER_SECRETS_FILE = temp_secrets_file.name  # reusing the temp file
            tc.USER_SECRETS_SALT_KEY = self.test_secret_key

            # Actually configuring the app
            current_app.config.from_object(tc)
            util.flush_caches()

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

    def test_secure_mode(self):
        """Vanilla test case for secure_mode

        Utility function for determining whether the app should start in secure mode
        """
        # Setting up config object
        tc = UtilsTestConfig()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            temp_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            tc.USER_SECRETS_FILE = temp_secrets_file.name  # reusing the temp file
            tc.USER_SECRETS_SALT_KEY = self.test_secret_key
            current_app.config.from_object(tc)
            util.flush_caches()

            secure_mode = util.secure_mode()

        self.assertTrue(secure_mode, "Secure mode not correctly detected")

        # The user secrets file shouldn't exist at this point
        secure_mode2 = util.secure_mode(flush_cache=True)
        self.assertFalse(secure_mode2, "Secure mode *shouldn't* be detected because the user secrets doesn't exist")

        # Testing that the salt not existing is
        tc.USER_SECRETS_SALT_KEY = "doesn't-exist"
        current_app.config.from_object(tc)
        secure_mode2 = util.secure_mode(flush_cache=False)
        self.assertFalse(secure_mode2, "Secure mode *shouldn't* be detected because the user secrets salt doesn't exist")

    def test_get_user_secrets(self):
        """Vanilla test case for get_user_secrets

        Utility function for reading user secrets from configured location
        """
        # Setting up config object
        tc = UtilsTestConfig()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file, \
                tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_user_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            json.dump(self.test_user_secrets, temp_user_secrets_file)
            temp_secrets_file.flush()
            temp_user_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            tc.USER_SECRETS_FILE = temp_user_secrets_file.name  # *not* reusing the temp file
            tc.USER_SECRETS_SALT_KEY = self.test_secret_key
            current_app.config.from_object(tc)

            util.get_secrets(flush_cache=True)
            util.get_user_secrets(flush_cache=True)
            util.secure_mode(flush_cache=True)
            user_secrets = util.get_user_secrets()

        self.assertDictEqual(user_secrets, self.test_user_secrets, "User secrets not loaded correctly")

    def test_auth_user(self):
        """Vanilla test case for auth_user

        Utility function for confirming that user matches what is in the records
        """
        # Setting up config object
        tc = UtilsTestConfig()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_secrets_file, \
                tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_user_secrets_file:
            json.dump(self.test_secrets, temp_secrets_file)
            json.dump(self.test_user_secrets, temp_user_secrets_file)
            temp_secrets_file.flush()
            temp_user_secrets_file.flush()

            tc.SECRETS_FILE = temp_secrets_file.name
            tc.USER_SECRETS_FILE = temp_user_secrets_file.name  # *not* reusing the temp file
            tc.USER_SECRETS_SALT_KEY = self.test_secret_key
            current_app.config.from_object(tc)

            util.get_secrets(flush_cache=True)
            util.get_user_secrets(flush_cache=True)
            util.secure_mode(flush_cache=True)
            user_auth_check = util.auth_user(self.test_secret_key, self.test_secret_value)

        self.assertTrue(user_auth_check, "User auth not successful")

        user_auth_check2 = util.auth_user(self.test_secret_key, "blah")
        self.assertFalse(user_auth_check2, "User auth successful despite the password being wrong!")

        user_auth_check3 = util.auth_user("foo", self.test_secret_value)
        self.assertFalse(user_auth_check2, "User auth successful despite the username being wrong!")


if __name__ == '__main__':
    import unittest

    unittest.main()
