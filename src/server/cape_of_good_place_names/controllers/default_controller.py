import connexion
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names.models.geolookup_results import GeolookupResults  # noqa: E501
from cape_of_good_place_names.models.scrub_results import ScrubResults  # noqa: E501
from cape_of_good_place_names import util


def geocode(address):  # noqa: E501
    """Translate a free form address into a spatial coordinate

     # noqa: E501

    :param address: Free form address string to geocode
    :type address: str

    :rtype: GeocodeResults
    """
    return 'do some magic!'


def geolookup(spatial_dataset_id, spatial_id=None):  # noqa: E501
    """Translate a spatial identifier into a description of space

     # noqa: E501

    :param spatial_dataset_id: dataset from which to look up spatial identifier
    :type spatial_dataset_id: str
    :param spatial_id: spatial identifier to look up in spatial dataset
    :type spatial_id: str

    :rtype: GeolookupResults
    """
    return 'do some magic!'


def scrub(address):  # noqa: E501
    """Extract meaningful phrases or identifiers from free form addresses

     # noqa: E501

    :param address: Free form address string
    :type address: str

    :rtype: ScrubResults
    """
    return 'do some magic!'
