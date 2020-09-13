# cape_of_good_place_names_client.DefaultApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**geocode**](DefaultApi.md#geocode) | **GET** /v1/geocode | Translate a free form address into a spatial coordinate
[**geolookup**](DefaultApi.md#geolookup) | **GET** /v1/boundary_lookup | Translate a spatial identifier into a description of space
[**scrub**](DefaultApi.md#scrub) | **GET** /v1/scrub | Extract meaningful phrases or identifiers from free form addresses


# **geocode**
> GeocodeResults geocode(address)

Translate a free form address into a spatial coordinate

### Example

* Basic Authentication (basicAuth):
```python
from __future__ import print_function
import time
import cape_of_good_place_names_client
from cape_of_good_place_names_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = cape_of_good_place_names_client.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = cape_of_good_place_names_client.Configuration(
    username = 'YOUR_USERNAME',
    password = 'YOUR_PASSWORD'
)

# Enter a context with an instance of the API client
with cape_of_good_place_names_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cape_of_good_place_names_client.DefaultApi(api_client)
    address = 'address_example' # str | Free form address string to geocode

    try:
        # Translate a free form address into a spatial coordinate
        api_response = api_instance.geocode(address)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->geocode: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**| Free form address string to geocode | 

### Return type

[**GeocodeResults**](GeocodeResults.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | An array of geocoded results |  -  |
**401** | Authentication information is missing or invalid |  * WWW_Authenticate -  <br>  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **geolookup**
> GeolookupResults geolookup(spatial_dataset_id, spatial_id=spatial_id)

Translate a spatial identifier into a description of space

### Example

* Basic Authentication (basicAuth):
```python
from __future__ import print_function
import time
import cape_of_good_place_names_client
from cape_of_good_place_names_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = cape_of_good_place_names_client.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = cape_of_good_place_names_client.Configuration(
    username = 'YOUR_USERNAME',
    password = 'YOUR_PASSWORD'
)

# Enter a context with an instance of the API client
with cape_of_good_place_names_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cape_of_good_place_names_client.DefaultApi(api_client)
    spatial_dataset_id = 'spatial_dataset_id_example' # str | dataset from which to look up spatial identifier
spatial_id = 'spatial_id_example' # str | spatial identifier to look up in spatial dataset (optional)

    try:
        # Translate a spatial identifier into a description of space
        api_response = api_instance.geolookup(spatial_dataset_id, spatial_id=spatial_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->geolookup: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **spatial_dataset_id** | **str**| dataset from which to look up spatial identifier | 
 **spatial_id** | **str**| spatial identifier to look up in spatial dataset | [optional] 

### Return type

[**GeolookupResults**](GeolookupResults.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | An array of geolookup results |  -  |
**401** | Authentication information is missing or invalid |  * WWW_Authenticate -  <br>  |
**404** | Either the spatial identifier or spatial dataset don&#39;t exist. |  -  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scrub**
> ScrubResults scrub(address)

Extract meaningful phrases or identifiers from free form addresses

### Example

* Basic Authentication (basicAuth):
```python
from __future__ import print_function
import time
import cape_of_good_place_names_client
from cape_of_good_place_names_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = cape_of_good_place_names_client.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = cape_of_good_place_names_client.Configuration(
    username = 'YOUR_USERNAME',
    password = 'YOUR_PASSWORD'
)

# Enter a context with an instance of the API client
with cape_of_good_place_names_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cape_of_good_place_names_client.DefaultApi(api_client)
    address = 'address_example' # str | Free form address string

    try:
        # Extract meaningful phrases or identifiers from free form addresses
        api_response = api_instance.scrub(address)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scrub: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**| Free form address string | 

### Return type

[**ScrubResults**](ScrubResults.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | An array of scrubbed results |  -  |
**401** | Authentication information is missing or invalid |  * WWW_Authenticate -  <br>  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

