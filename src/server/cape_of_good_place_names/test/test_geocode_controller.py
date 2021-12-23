# coding: utf-8

from __future__ import absolute_import
import base64
import os
import tempfile

from flask import json, current_app
from geocode_array.Geocoder import Geocoder
from six import BytesIO

from cape_of_good_place_names import util
from cape_of_good_place_names.config import config
from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class MockGeocoder(Geocoder):
    X = 0.0001
    Y = 0.000
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, self.X, self.Y, None


class MockGeocoder2(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, 0.0001, 0.0001, None


class BadMockGeocoder(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, None, "", None


class GeocoderTestConfig:
    TIMEZONE = "Africa/Johannesburg"
    GEOCODERS = [
        (
            MockGeocoder, {}
        ),
    ]
    GEOCODER_CACHE_DIR = None
    GEOCODER_CACHE_AGE_THRESHOLD = 1000
    GEOCODERS_MIN = 1
    USER_SECRETS_FILE = ""
    USER_SECRETS_SALT_KEY = ""
    SCRUBBERS = []
    SCRUBBERS_MIN = 0


class TestGeocodeController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

        # Setting up cache dir
        self.tempdir = tempfile.TemporaryDirectory()
        GeocoderTestConfig.GEOCODER_CACHE_DIR = self.tempdir.name

        for gc in [MockGeocoder, MockGeocoder2, BadMockGeocoder]:
            gc_cache_path = os.path.join(self.tempdir.name, gc.__name__)
            os.mkdir(gc_cache_path)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_geocoders(self):
        """Vanilla test case for geocoders

        Return list of supported geocoder IDs
        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
            (
                MockGeocoder2, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        response = self.client.open(
            '/v1.1/geocoders',
            method='GET',
            headers=self.authorisation_headers
        )
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Asserting that we get back the results we expect
        data_list = json.loads(response.data)
        self.assertListEqual([MockGeocoder.__name__, MockGeocoder2.__name__], data_list)

    def test_geocode(self):
        """Vanilla test case for geocode

        Translate a free form address into a spatial coordinate
        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Asserting that we get back the results we expect
        data_dict = json.loads(response.data)
        self.assertIn("results", data_dict)
        results = data_dict["results"]
        self.assertEqual(2, len(data_dict["results"]), "Geocoder is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["geocoder_id"], MockGeocoder.__name__, "Geocode ID not mapped through correctly")
        self.assertEqual(result["confidence"], 1, "Geocoder confidence not mapped through correctly")
        result_dict = json.loads(result["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.000, 0.0001], "type": "Point"},
                 "properties": {"address": "address_example"}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict,
            "Geocoded value not mapped through correctly"
        )

        # Inspecting the second result (the combined result)
        *_, result2 = results
        result_dict2 = json.loads(result2["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0001], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict2,
            "Combined geocoded value not mapped through correctly"

        )

        # Checking that the cache is getting populated
        for gc, _ in tc.GEOCODERS:
            cache_path = os.path.join(self.tempdir.name, gc.__name__)
            cache_files = os.listdir(cache_path)
            self.assertEqual(len(cache_files), 1, "Cache result file not getting created as expected!")

    def test_geocode_cache(self):
        """Tests that geocode cache is being used

        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        data_dict = json.loads(response.data)
        results = data_dict["results"]
        result, *_ = results
        result_dict = json.loads(result["geocoded_value"])

        # Checking that the cache is getting populated
        for gc, _ in tc.GEOCODERS:
            cache_path = os.path.join(self.tempdir.name, gc.__name__)
            cache_files = os.listdir(cache_path)
            self.assertEqual(len(cache_files), 1, "Cache result file not getting created as expected!")

        geocoder_tuple, *_ = tc.GEOCODERS
        geocoder_class, _ = geocoder_tuple
        geocoder_class.X = 5
        geocoder_class.Y = 10

        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        data_dict = json.loads(response.data)
        results = data_dict["results"]
        result, *_ = results
        result_dict2 = json.loads(result["geocoded_value"])
        self.assertDictEqual(result_dict, result_dict2, "Second read not getting cached value!")



    def test_combined_geocode(self):
        """Testing that combined geocode result is blended into results

        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
            (
                MockGeocoder2, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )

        data_dict = json.loads(response.data)
        results = data_dict["results"]
        self.assertEqual(3, len(results), "Geocoder is not returning the expected number of test results")

        *_, combined_result = results
        result_dict = json.loads(combined_result["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.00005, 0.0001], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder", "MockGeocoder2"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict,
            "Combined geocoded value not mapped through correctly"
        )

    def test_geocode_with_specified_geocoders(self):
        """Testing that only configured geocoders are included in results

        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
            (
                MockGeocoder2, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        query_string = [('address', 'address_example'), ('geocoders', 'MockGeocoder2',)]
        response = self.client.open(
            '/v1.1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        data_dict = json.loads(response.data)
        results = data_dict["results"]
        self.assertEqual(2, len(results), "Geocoder is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["geocoder_id"], MockGeocoder2.__name__, "Geocode ID not mapped through correctly")
        self.assertEqual(result["confidence"], 1, "Geocoder confidence not mapped through correctly")
        result_dict = json.loads(result["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.0001, 0.0001], "type": "Point"},
                 "properties": {"address": "address_example"}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict,
            "Geocoded value not mapped through correctly"
        )

        # Inspecting the second result (the combined result)
        *_, result2 = results
        result_dict2 = json.loads(result2["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.0001, 0.0001], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder2"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict2,
            "Combined geocoded value not mapped through correctly"
        )

    def test_bad_gecode(self):
        """Testing the behaviour around failed geocoding AKA SAD CASE TESTS

        """
        tc = GeocoderTestConfig()
        tc.GEOCODERS = [
            (
                MockGeocoder, {}
            ),
            (
                BadMockGeocoder, {}
            ),
        ]
        current_app.config.from_object(tc)
        util.flush_caches()

        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )

        data_dict = json.loads(response.data)
        results = data_dict["results"]
        # For now, the expected behaviour is just to pass through failed geocodes with null values.
        self.assertEqual(3, len(results), "Geocoder is not returning the expected number of test results")

        _, bad_result, _ = results
        self.assertEqual(bad_result["confidence"], 0, "Failed geocoder confidence not mapped through correctly")
        result = json.loads(bad_result["geocoded_value"])
        self.assertIsNone(result, "Failed geocoder not returning a null result")

        *_, combined_result = results
        result_dict = json.loads(combined_result["geocoded_value"])
        self.assertDictEqual(
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0001], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            result_dict,
            "Combined geocoded value not excluding bad geocoder properly"
        )


if __name__ == '__main__':
    import unittest

    unittest.main()
