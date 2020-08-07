# coding: utf-8

from __future__ import absolute_import
import base64

from flask import json, current_app
from six import BytesIO

from cape_of_good_place_names.test import BaseTestCase


class MockScrubber:

    def __init__(self): pass

    def scrub(self, value):
        return value + ", niks"


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": "Basic {}".format(credentials)}
        current_app.config["SCRUBBERS"] = [MockScrubber]

    def test_scrub(self):
        """Vanilla test case for scrub

        Extract meaningful phrases or identifiers from free form addresses
        """
        # Asserting that we at least get a 200 back
        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/scrub',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Asserting that we get back the results we expect
        data_dict = json.loads(response.data)
        self.assertIn("results", data_dict)
        results = data_dict["results"]
        self.assertEqual(len(results), 1, "Scrubber is not returning the expected number of test results")

        # Inspecting the result itself
        result, *_ = results
        self.assertEqual(result["scrubber_id"], MockScrubber.__name__, "Scrubber ID not mapped through correctly")
        self.assertDictEqual(
            result,
            {'scrubbed_value': 'address_example, niks', 'scrubber_id': 'MockScrubber'},
            "Geocoded value not mapped through correctly"
        )


if __name__ == '__main__':
    import unittest

    unittest.main()
