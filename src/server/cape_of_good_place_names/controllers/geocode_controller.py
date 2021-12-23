import pprint

from flask import current_app, json
from geocode_array import geocode_array

from cape_of_good_place_names.models.geocode_result import GeocodeResult
from cape_of_good_place_names.models.geocode_results import GeocodeResults  # noqa: E501
from cape_of_good_place_names import util


def geocoders():  # noqa: E501
    """Return list of supported geocoder IDs

     # noqa: E501


    :rtype: List[str]
    """
    geocoder_names = [geocoder.__class__.__name__ for geocoder in util.get_geocoders()]
    return geocoder_names


def geocode_v1(address):  # noqa: E501
    """Translate a free form address into a spatial coordinate

     # noqa: E501

    :param address: Free form address string to geocode
    :type address: str
    :param geocoders: ID of Geocoders that should be used
    :type geocoders: List[str]

    :rtype: GeocodeResults
    """
    return geocode(address)


def geocode(address, geocoders=None):  # noqa: E501
    """Translate a free form address into a spatial coordinate

     # noqa: E501

    :param address: Free form address string to geocode
    :type address: str

    :rtype: GeocodeResults
    """
    request_timestamp = util.get_timestamp()
    current_app.logger.info("Geocod[ing]...")
    current_app.logger.debug("address='{}'".format(address))

    # Actually doing the geocoding
    geocoder_classes = [
        geocoder for geocoder in util.get_geocoders()
        if (geocoders is None) or
           (geocoders and geocoder.__class__.__name__ in geocoders)
    ]
    raw_geocoder_results = [result for result in geocode_array.threaded_geocode(geocoder_classes, address)]
    geocoder_results = [
        (
            {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [result[2], result[1]]  # converting Geocoder (lat, long) -> GeoJSON Point (x, y)
                    },
                    "properties": {
                        "address": result[0]
                    }
                }]
            } if result[1] is not None
            else None
        )
        for result in raw_geocoder_results
    ]
    current_app.logger.debug("geocoder_results=\n'{}'".format(pprint.pformat(geocoder_results)))

    response_results = [
        GeocodeResult(geocoder.__class__.__name__, json.dumps(geocoder_result), 1 if geocoder_result else 0)
        for geocoder, geocoder_result in zip(geocoder_classes, geocoder_results)
    ]

    # Merging in a combined result
    combined_result = geocode_array.combine_geocode_results(
        [
            (gc.__class__.__name__, *result_tuple)
            for gc, result_tuple in zip(geocoder_classes, raw_geocoder_results)
            if None not in result_tuple[:3]
        ]
    )
    current_app.logger.debug("combined_result=\n'{}'".format(pprint.pformat(combined_result)))

    if combined_result and None not in combined_result[:2]:
        current_app.logger.debug("Adding in combined_result")
        combined_confidence = 1
        combined_confidence -= (
                (geocode_array.DISPERSION_THRESHOLD - combined_result[2]) /
                geocode_array.DISPERSION_THRESHOLD
        )

        response_results += [
            GeocodeResult("CombinedGeocoders",
                          json.dumps({
                              "type": "FeatureCollection",
                              "features": [{
                                  "type": "Feature",
                                  "geometry": {
                                      "type": "Point",
                                      "coordinates": [combined_result[1], combined_result[0]]
                                  },
                                  "properties": {
                                      "geocoders": combined_result[-1]
                                  }
                              }]
                          }), combined_confidence)
        ]
    else:
        current_app.logger.warning("Combined result not merged in")

    response = GeocodeResults(
        id=util.get_request_uuid(),
        timestamp=request_timestamp,
        results=response_results
    )
    current_app.logger.info("...Geocod[ed]".format(address))

    return response
