import connexion
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
    return 'do some magic!'
