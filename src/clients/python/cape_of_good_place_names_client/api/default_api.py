# coding: utf-8

"""
    Cape of Good Place Names Service

    This is a stateless service for performing various geotranslation operations, moving between how people describe places and codified coordinate systems.  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Contact: opmdata+cogpn-support@capetown.gov.za
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from cape_of_good_place_names_client.api_client import ApiClient
from cape_of_good_place_names_client.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class DefaultApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def geocode(self, address, **kwargs):  # noqa: E501
        """Translate a free form address into a spatial coordinate  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.geocode(address, async_req=True)
        >>> result = thread.get()

        :param address: Free form address string to geocode (required)
        :type address: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: GeocodeResults
        """
        kwargs['_return_http_data_only'] = True
        return self.geocode_with_http_info(address, **kwargs)  # noqa: E501

    def geocode_with_http_info(self, address, **kwargs):  # noqa: E501
        """Translate a free form address into a spatial coordinate  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.geocode_with_http_info(address, async_req=True)
        >>> result = thread.get()

        :param address: Free form address string to geocode (required)
        :type address: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(GeocodeResults, status_code(int), headers(HTTPHeaderDict))
        """

        local_var_params = locals()

        all_params = [
            'address'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method geocode" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'address' is set
        if self.api_client.client_side_validation and ('address' not in local_var_params or  # noqa: E501
                                                        local_var_params['address'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `address` when calling `geocode`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'address' in local_var_params and local_var_params['address'] is not None:  # noqa: E501
            query_params.append(('address', local_var_params['address']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return self.api_client.call_api(
            '/v1/geocode', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='GeocodeResults',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))

    def geolookup(self, spatial_dataset_id, **kwargs):  # noqa: E501
        """Translate a spatial identifier into a description of space  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.geolookup(spatial_dataset_id, async_req=True)
        >>> result = thread.get()

        :param spatial_dataset_id: dataset from which to look up spatial identifier (required)
        :type spatial_dataset_id: str
        :param spatial_id: spatial identifier to look up in spatial dataset
        :type spatial_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: GeolookupResults
        """
        kwargs['_return_http_data_only'] = True
        return self.geolookup_with_http_info(spatial_dataset_id, **kwargs)  # noqa: E501

    def geolookup_with_http_info(self, spatial_dataset_id, **kwargs):  # noqa: E501
        """Translate a spatial identifier into a description of space  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.geolookup_with_http_info(spatial_dataset_id, async_req=True)
        >>> result = thread.get()

        :param spatial_dataset_id: dataset from which to look up spatial identifier (required)
        :type spatial_dataset_id: str
        :param spatial_id: spatial identifier to look up in spatial dataset
        :type spatial_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(GeolookupResults, status_code(int), headers(HTTPHeaderDict))
        """

        local_var_params = locals()

        all_params = [
            'spatial_dataset_id',
            'spatial_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method geolookup" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'spatial_dataset_id' is set
        if self.api_client.client_side_validation and ('spatial_dataset_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['spatial_dataset_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `spatial_dataset_id` when calling `geolookup`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'spatial_id' in local_var_params and local_var_params['spatial_id'] is not None:  # noqa: E501
            query_params.append(('spatial_id', local_var_params['spatial_id']))  # noqa: E501
        if 'spatial_dataset_id' in local_var_params and local_var_params['spatial_dataset_id'] is not None:  # noqa: E501
            query_params.append(('spatial_dataset_id', local_var_params['spatial_dataset_id']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return self.api_client.call_api(
            '/v1/boundary_lookup', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='GeolookupResults',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))

    def scrub(self, address, **kwargs):  # noqa: E501
        """Extract meaningful phrases or identifiers from free form addresses  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.scrub(address, async_req=True)
        >>> result = thread.get()

        :param address: Free form address string (required)
        :type address: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: ScrubResults
        """
        kwargs['_return_http_data_only'] = True
        return self.scrub_with_http_info(address, **kwargs)  # noqa: E501

    def scrub_with_http_info(self, address, **kwargs):  # noqa: E501
        """Extract meaningful phrases or identifiers from free form addresses  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.scrub_with_http_info(address, async_req=True)
        >>> result = thread.get()

        :param address: Free form address string (required)
        :type address: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(ScrubResults, status_code(int), headers(HTTPHeaderDict))
        """

        local_var_params = locals()

        all_params = [
            'address'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method scrub" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'address' is set
        if self.api_client.client_side_validation and ('address' not in local_var_params or  # noqa: E501
                                                        local_var_params['address'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `address` when calling `scrub`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'address' in local_var_params and local_var_params['address'] is not None:  # noqa: E501
            query_params.append(('address', local_var_params['address']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return self.api_client.call_api(
            '/v1/scrub', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='ScrubResults',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))
