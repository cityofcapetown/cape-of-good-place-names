import base64
import datetime
import pathlib
import pickle
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


def _get_cache_path(geocoder, address):
    address_filename = base64.b64encode(address.encode()).decode() + ".pickle.gz"
    cache_path = pathlib.Path(current_app.config["GEOCODER_CACHE_DIR"]) / geocoder.__class__.__name__ / address_filename

    return cache_path


def _get_cached_result(geocoder, address):
    cache_path = _get_cache_path(geocoder, address)
    current_app.logger.debug(f"{geocoder.__class__.__name__} + '{address}' -> '{cache_path}'")

    creation_threshold = current_app.config["GEOCODER_CACHE_AGE_THRESHOLD"]
    now = datetime.datetime.now()
    if cache_path.exists() and (now.timestamp() - cache_path.stat().st_ctime) < creation_threshold:
        current_app.logger.debug(f"Found '{cache_path}' for '{address}', newer than {creation_threshold} seconds, using it")
        with open(cache_path, 'rb') as cache_file:
            return pickle.load(cache_file)
    elif cache_path.exists():
        current_app.logger.debug(f"Found '{cache_path}', but it is too old")
    else:
        current_app.logger.debug(f"Didn't find '{cache_path}'")

    return None


def _update_cache(geocoder, address, result):
    cache_path = _get_cache_path(geocoder, address)
    current_app.logger.debug(f"Writing '{cache_path}'")

    with open(cache_path, "wb") as cache_file:
        pickle.dump(result, cache_file)
        cache_file.flush()

    return result


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
    cached_results = dict(filter(lambda tup: tup[1], (
        (geocoder, _get_cached_result(geocoder, address))
        for geocoder in geocoder_classes
    )))
    fresh_results = {
        geocoder: _update_cache(geocoder, address, result)
        for geocoder, result in
        zip(geocoder_classes, geocode_array.threaded_geocode(geocoder_classes, address))
        if geocoder not in cached_results
    }
    combined_results = {**cached_results, **fresh_results}
    geocoder_results = {
        geocoder: (
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
        for geocoder, result in combined_results.items()
    }
    current_app.logger.debug("geocoder_results=\n'{pprint.pformat(geocoder_results)}'")

    response_results = [
        GeocodeResult(geocoder.__class__.__name__, json.dumps(geocoder_result), 1 if geocoder_result else 0)
        for geocoder, geocoder_result in geocoder_results.items()
    ]

    # Merging in a combined result
    combined_result = geocode_array.combine_geocode_results(
        [
            (gc.__class__.__name__, *result_tuple)
            for gc, result_tuple in combined_results.items()
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
