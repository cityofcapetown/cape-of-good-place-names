# coding: utf-8

"""
    Cape of Good Place Names Service

    This is a stateless service for performing various geotranslation operations, moving between how people describe places and codified coordinate systems.  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Contact: opmdata+cogpn-support@capetown.gov.za
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from cape_of_good_place_names_client.configuration import Configuration


class GeocodeResults(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'id': 'str',
        'timestamp': 'datetime',
        'results': 'list[GeocodeResult]'
    }

    attribute_map = {
        'id': 'id',
        'timestamp': 'timestamp',
        'results': 'results'
    }

    def __init__(self, id=None, timestamp=None, results=None, local_vars_configuration=None):  # noqa: E501
        """GeocodeResults - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._timestamp = None
        self._results = None
        self.discriminator = None

        self.id = id
        self.timestamp = timestamp
        self.results = results

    @property
    def id(self):
        """Gets the id of this GeocodeResults.  # noqa: E501

        UUID describing the transaction  # noqa: E501

        :return: The id of this GeocodeResults.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this GeocodeResults.

        UUID describing the transaction  # noqa: E501

        :param id: The id of this GeocodeResults.  # noqa: E501
        :type id: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def timestamp(self):
        """Gets the timestamp of this GeocodeResults.  # noqa: E501

        Server time of the transaction  # noqa: E501

        :return: The timestamp of this GeocodeResults.  # noqa: E501
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this GeocodeResults.

        Server time of the transaction  # noqa: E501

        :param timestamp: The timestamp of this GeocodeResults.  # noqa: E501
        :type timestamp: datetime
        """
        if self.local_vars_configuration.client_side_validation and timestamp is None:  # noqa: E501
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

    @property
    def results(self):
        """Gets the results of this GeocodeResults.  # noqa: E501

        Array of Geocoding results  # noqa: E501

        :return: The results of this GeocodeResults.  # noqa: E501
        :rtype: list[GeocodeResult]
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this GeocodeResults.

        Array of Geocoding results  # noqa: E501

        :param results: The results of this GeocodeResults.  # noqa: E501
        :type results: list[GeocodeResult]
        """
        if self.local_vars_configuration.client_side_validation and results is None:  # noqa: E501
            raise ValueError("Invalid value for `results`, must not be `None`")  # noqa: E501

        self._results = results

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GeocodeResults):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GeocodeResults):
            return True

        return self.to_dict() != other.to_dict()
