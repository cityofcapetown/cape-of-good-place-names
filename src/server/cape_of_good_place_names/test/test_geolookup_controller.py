# coding: utf-8

from __future__ import absolute_import
import base64
import tempfile

from flask import json, current_app
from six import BytesIO

from cape_of_good_place_names import util
from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geolookup_results import GeolookupResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class GeoLookupTestConfig(object):
    TIMEZONE = "Africa/Johannesburg"
    USER_SECRETS_FILE = ""
    USER_SECRETS_SALT_KEY = ""


class TestGeoLookupController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}

        # Setting up the GeoLookup data files
        tc = GeoLookupTestConfig()

        self.temp_dir = tempfile.TemporaryDirectory()
        tc.GEOLOOKUP_DATASET_DIR = self.temp_dir.name

        temp_geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [0.0, 0.0]
                },
                "properties": {
                    "temp_id": "centre_of_the_world"
                }}]
        }
        temp_layer_file_path = self.temp_dir.name + "temp_layer.geojson"
        with open(temp_layer_file_path, "w") as temp_layer_file:
            json.dump(temp_geojson, temp_layer_file)

        tc.GEOLOOKUP_DATASET_CONFIG = {
            "temp_layer": (temp_layer_file.name, "temp_id")
        }
        current_app.config.from_object(tc)
        util.flush_caches()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_geolookup(self):
        """Vanilla test case for geolookup of specific ID

        Translate a spatial identifier into a description of space
        """
        # Looking up a specific ID
        query_string = [('spatial_id', 'centre_of_the_world'),
                        ('spatial_dataset_id', 'temp_layer')]
        response = self.client.open(
            '/v1/boundary_lookup',
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
        self.assertEqual(len(data_dict["results"]), 1,
                         "Boundary Lookup is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["geolookup_id"], "centre_of_the_world", "Spatial ID not mapped through correctly")
        result_dict = json.loads(result["geolookup_value"])
        self.assertEqual(
            result_dict,
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"},
                 "properties": {"temp_id": "centre_of_the_world"}, "type": "Feature"}],
             "type": "FeatureCollection"},
            "Geolookedup value not mapped through correctly"
        )

    def test_geolookup_dataset(self):
        """Vanilla test case for geolookup of whole dataset

        Translate a spatial identifier into a description of space
        """
        # Looking up a specific ID
        query_string = [('spatial_dataset_id', 'temp_layer')]
        response = self.client.open(
            '/v1/boundary_lookup',
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
        self.assertEqual(len(data_dict["results"]), 1,
                         "Boundary Lookup is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["geolookup_id"], "temp_layer", "Spatial Dataset ID not mapped through correctly")
        result_dict = json.loads(result["geolookup_value"])
        self.assertEqual(
            result_dict,
            {"features": [
                {"geometry": {"coordinates": [0.0, 0.0], "type": "Point"},
                 "properties": {"temp_id": "centre_of_the_world"}, "type": "Feature"}],
                "type": "FeatureCollection"},
            "Geolookedup value not mapped through correctly"
        )


if __name__ == '__main__':
    import unittest

    unittest.main()
