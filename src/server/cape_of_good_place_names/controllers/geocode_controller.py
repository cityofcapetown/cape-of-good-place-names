import logging
import pprint

import connexion
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names import util


def geocode(address):  # noqa: E501
    """Translate a free form address into a spatial coordinate

     # noqa: E501

    :param address: Free form address string to geocode
    :type address: str

    :rtype: GeocodeResults
    """
    request_id = util.get_request_uuid()
    request_timestamp = util.get_timestamp()

    response = GeocodeResults(
        id=request_id,
        timestamp=request_timestamp,
        results=[]
    )

    return response
