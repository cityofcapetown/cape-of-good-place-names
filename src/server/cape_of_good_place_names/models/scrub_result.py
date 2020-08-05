# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from cape_of_good_place_names.models.base_model_ import Model
from cape_of_good_place_names import util


class ScrubResult(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, scrubber_id: str=None, scrubbed_value: str=None, confidence: float=None):  # noqa: E501
        """ScrubResult - a model defined in Swagger

        :param scrubber_id: The scrubber_id of this ScrubResult.  # noqa: E501
        :type scrubber_id: str
        :param scrubbed_value: The scrubbed_value of this ScrubResult.  # noqa: E501
        :type scrubbed_value: str
        :param confidence: The confidence of this ScrubResult.  # noqa: E501
        :type confidence: float
        """
        self.swagger_types = {
            'scrubber_id': str,
            'scrubbed_value': str,
            'confidence': float
        }

        self.attribute_map = {
            'scrubber_id': 'scrubber_id',
            'scrubbed_value': 'scrubbed_value',
            'confidence': 'confidence'
        }
        self._scrubber_id = scrubber_id
        self._scrubbed_value = scrubbed_value
        self._confidence = confidence

    @classmethod
    def from_dict(cls, dikt) -> 'ScrubResult':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ScrubResult of this ScrubResult.  # noqa: E501
        :rtype: ScrubResult
        """
        return util.deserialize_model(dikt, cls)

    @property
    def scrubber_id(self) -> str:
        """Gets the scrubber_id of this ScrubResult.

        Identifier for the scrubber  # noqa: E501

        :return: The scrubber_id of this ScrubResult.
        :rtype: str
        """
        return self._scrubber_id

    @scrubber_id.setter
    def scrubber_id(self, scrubber_id: str):
        """Sets the scrubber_id of this ScrubResult.

        Identifier for the scrubber  # noqa: E501

        :param scrubber_id: The scrubber_id of this ScrubResult.
        :type scrubber_id: str
        """
        if scrubber_id is None:
            raise ValueError("Invalid value for `scrubber_id`, must not be `None`")  # noqa: E501

        self._scrubber_id = scrubber_id

    @property
    def scrubbed_value(self) -> str:
        """Gets the scrubbed_value of this ScrubResult.


        :return: The scrubbed_value of this ScrubResult.
        :rtype: str
        """
        return self._scrubbed_value

    @scrubbed_value.setter
    def scrubbed_value(self, scrubbed_value: str):
        """Sets the scrubbed_value of this ScrubResult.


        :param scrubbed_value: The scrubbed_value of this ScrubResult.
        :type scrubbed_value: str
        """
        if scrubbed_value is None:
            raise ValueError("Invalid value for `scrubbed_value`, must not be `None`")  # noqa: E501

        self._scrubbed_value = scrubbed_value

    @property
    def confidence(self) -> float:
        """Gets the confidence of this ScrubResult.


        :return: The confidence of this ScrubResult.
        :rtype: float
        """
        return self._confidence

    @confidence.setter
    def confidence(self, confidence: float):
        """Sets the confidence of this ScrubResult.


        :param confidence: The confidence of this ScrubResult.
        :type confidence: float
        """
        if confidence is None:
            raise ValueError("Invalid value for `confidence`, must not be `None`")  # noqa: E501

        self._confidence = confidence
