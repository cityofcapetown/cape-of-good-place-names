import functools
import os
import pprint

import connexion
from flask import current_app, json
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.geolookup_results import GeolookupResults  # noqa: E501
from cape_of_good_place_names.models.geolookup_result import GeolookupResult  # noqa: E501
from cape_of_good_place_names import util


@functools.lru_cache()
def _load_geolookup_dataset(lookup_filename, id_property):
    dir_path = current_app.config["GEOLOOKUP_DATASET_DIR"]
    lookup_path = os.path.join(dir_path, lookup_filename)
    assert os.path.exists(lookup_path), f"Lookup dataset '{lookup_filename}' doesn't exit!"

    with open(lookup_path) as lookup_file:
        lookup_data = json.load(lookup_file)

    return {
        lookup_item["properties"][id_property]: lookup_item
        for lookup_item in lookup_data["features"]
    }, lookup_data


def geolookup(spatial_dataset_id, spatial_id=None):  # noqa: E501
    """Translate a spatial identifier into a description of space

     # noqa: E501
k
    :param spatial_dataset_id: dataset from which to look up spatial identifier
    :type spatial_dataset_id: str
    :param spatial_id: spatial identifier to look up in spatial dataset
    :type spatial_id: str

    :rtype: GeolookupResults
    """
    request_timestamp = util.get_timestamp()
    current_app.logger.info("Geolook[ing] up...")
    current_app.logger.debug(f"spatial_dataset_id='{spatial_dataset_id}', spatial_id='{spatial_id}'")

    # Loading the dataset
    geolookup_config = current_app.config["GEOLOOKUP_DATASET_CONFIG"]
    if spatial_dataset_id not in geolookup_config:
        return Error(code=404, message=f"'{spatial_dataset_id}' is doesn't exist on this server!")

    dataset_filename, property_id = geolookup_config[spatial_dataset_id]
    spatial_lookup, spatial_dataset = _load_geolookup_dataset(dataset_filename, property_id)

    if spatial_id:
        if spatial_id not in spatial_lookup:
            return Error(code=404, message=f"'{spatial_id}' is not in '{spatial_dataset_id}'!")

        lookup_id = spatial_id
        lookup_result = {
            "type": "FeatureCollection",
            "features": [
                spatial_lookup[spatial_id]
            ]
        }
        current_app.logger.debug(f"lookup_result=\n'{pprint.pformat(lookup_result)}', lookup_id='{lookup_id}'")
    else:
        lookup_id = spatial_dataset_id
        lookup_result = spatial_dataset
        current_app.logger.debug(f"lookup_id='{lookup_id}'")

    # Forming the response
    geolookup_result = GeolookupResult(
        geolookup_id=lookup_id,
        geolookup_value=json.dumps(lookup_result)
    )

    response = GeolookupResults(
        id=util.get_request_uuid(),
        timestamp=request_timestamp,
        results=[geolookup_result]
    )
    current_app.logger.info("...Geolook[ed] up!")

    return response
