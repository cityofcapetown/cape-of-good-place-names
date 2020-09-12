# coding: utf-8

from __future__ import absolute_import
import base64

from flask import json, current_app
from geocode_array.Geocoder import Geocoder
from six import BytesIO

from cape_of_good_place_names import util
from cape_of_good_place_names.config import config
from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class MockGeocoder(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, 0, 0, None


class MockGeocoder2(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, 0.0001, 0.0001, None


class BadMockGeocoder(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, None, "", None


class GeocoderTestConfig(object):
    TIMEZONE = "Africa/Johannesburg"
    GEOCODERS = [
        (
            MockGeocoder, {}
        ),
    ]
    GEOCODERS_MIN = 1
    USER_SECRETS_FILE = ""
    USER_SECRETS_SALT_KEY = ""


class TestGeocodeController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

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
            result_dict,
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"},
                 "properties": {"address": "address_example"}, "type": "Feature"}],
                "type": "FeatureCollection"},
            "Geocoded value not mapped through correctly"
        )

        # Inspecting the second result (the combined result)
        *_, result2 = results
        result_dict2 = json.loads(result2["geocoded_value"])
        self.assertDictEqual(
            result_dict2,
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            "Combined geocoded value not mapped through correctly"
        )

    def test_combined_gecode(self):
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
            result_dict,
            {"features": [
                {"geometry": {"coordinates": [0.00005, 0.00005], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder", "MockGeocoder2"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
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
            result_dict,
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"},
                 "properties": {"geocoders": ["MockGeocoder"]}, "type": "Feature"}],
                "type": "FeatureCollection"},
            "Combined geocoded value not excluding bad geocoder properly"
        )


if __name__ == '__main__':
    import unittest

    unittest.main()
