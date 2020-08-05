# coding: utf-8

from __future__ import absolute_import
import base64

from flask import json
from six import BytesIO

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geolookup_results import GeolookupResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        credentials = base64.b64encode(b"test_user:test_password").decode('utf-8')
        self.authorisation_headers = {"Authorization": f"Basic {credentials}"}

    def test_geolookup(self):
        """Test case for geolookup

        Translate a spatial identifier into a description of space
        """
        query_string = [('spatial_id', 'spatial_id_example'),
                        ('spatial_dataset_id', 'spatial_dataset_id_example')]
        response = self.client.open(
            '/v1/boundary_lookup',
            method='GET',
            query_string=query_string,
            headers=self.authorisation_headers
        )
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()