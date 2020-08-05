import connexion
from flask import current_app
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.scrub_results import ScrubResults  # noqa: E501
from cape_of_good_place_names import util


def scrub(address):  # noqa: E501
    """Extract meaningful phrases or identifiers from free form addresses

     # noqa: E501

    :param address: Free form address string
    :type address: str

    :rtype: ScrubResults
    """
    request_id = util.get_request_uuid()
    request_timestamp = util.get_timestamp()

    response = ScrubResults(
        id=request_id,
        timestamp=request_timestamp,
        results=[]
    )

    return response
