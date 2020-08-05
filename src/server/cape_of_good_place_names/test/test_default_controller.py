# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.models.geolookup_results import GeolookupResults  # noqa: E501
from cape_of_good_place_names.models.scrub_results import ScrubResults  # noqa: E501
from cape_of_good_place_names.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_geocode(self):
        """Test case for geocode

        Translate a free form address into a spatial coordinate
        """
        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/geocode',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_geolookup(self):
        """Test case for geolookup

        Translate a spatial identifier into a description of space
        """
        query_string = [('spatial_id', 'spatial_id_example'),
                        ('spatial_dataset_id', 'spatial_dataset_id_example')]
        response = self.client.open(
            '/v1/boundary_lookup',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_scrub(self):
        """Test case for scrub

        Extract meaningful phrases or identifiers from free form addresses
        """
        query_string = [('address', 'address_example')]
        response = self.client.open(
            '/v1/scrub',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
