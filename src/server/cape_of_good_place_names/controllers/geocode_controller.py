import collections
import logging
import pprint

import connexion
from flask import current_app, json
from geocode_array import geocode_array
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_result import GeocodeResult
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names import util


def geocode(address):  # noqa: E501
    """Translate a free form address into a spatial coordinate

     # noqa: E501

    :param address: Free form address string to geocode
    :type address: str

    :rtype: GeocodeResults
    """
    request_timestamp = util.get_timestamp()

    # Actually doing the geocoding
    geocoders = [gc() for gc in current_app.config["GEOCODERS"]]
    geocoder_results = (
        (
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [result[1], result[2]]
                },
                "properties": {
                    "address": result[0]
                }
            } if result[1] is not None
            else None
        )
        for result in geocode_array.threaded_geocode(geocoders, address)
    )

    response_results = [
        GeocodeResult(geocoder.__class__.__name__, json.dumps(geocoder_result), 1 if geocoder_result else 0)
        for geocoder, geocoder_result in zip(geocoders, geocoder_results)
    ]

    response = GeocodeResults(
        id=util.get_request_uuid(),
        timestamp=request_timestamp,
        results=response_results
    )

    return response
