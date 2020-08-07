# coding: utf-8

from __future__ import absolute_import
import base64

from flask import json
from six import BytesIO

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase, MockGeocoder


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

        current_app.config["GEOCODERS"] = [MockGeocoder]

    def test_geocode(self):
        """Vanilla test case for geocode

        Translate a free form address into a spatial coordinate
        """
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
        self.assertEqual(len(data_dict["results"]), 1, "Geocoder is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["geocoder_id"], MockGeocoder.__name__, "Geocode ID not mapped through correctly")
        self.assertEqual(result["confidence"], 1, "Geocoder confidence not mapped through correctly")
        self.assertEqual(
            result["geocoded_value"],
            '{"features": {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"}, "properties": {"address": "address_example"}, "type": "Feature"}, "type": "FeatureCollection"}',
            "Geocoded value not mapped through correctly"
        )


if __name__ == '__main__':
    import unittest

    unittest.main()
