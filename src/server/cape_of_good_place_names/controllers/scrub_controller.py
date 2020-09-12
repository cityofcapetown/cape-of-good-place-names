import pprint

import connexion
from flask import current_app
import six

from cape_of_good_place_names.models.error import Error  # noqa: E501
from cape_of_good_place_names.models.scrub_result import ScrubResult  # noqa: E501
from cape_of_good_place_names.models.scrub_results import ScrubResults  # noqa: E501
from cape_of_good_place_names import util


def scrub(address):  # noqa: E501
    """Extract meaningful phrases or identifiers from free form addresses

     # noqa: E501

    :param address: Free form address string
    :type address: str

    :rtype: ScrubResults
    """
    request_timestamp = util.get_timestamp()
    current_app.logger.info("Scrubb[ing]...")
    current_app.logger.debug(f"address='{address}'")

    scrubbers = util.get_scrubbers()
    scrubbed_values = [
        scrubber.scrub(address)
        for scrubber in scrubbers
    ]
    current_app.logger.debug(f"scrubbed_values=\n{pprint.pformat(scrubbed_values)}")

    scrub_results = (
        ScrubResult(
            scrubber_id=scrubber.__class__.__name__,
            scrubbed_value=scrubbed_value,
            confidence=scubber_confidence
        )
        for scrubber, (scrubbed_value, scubber_confidence) in zip(scrubbers, scrubbed_values)
    )

    response = ScrubResults(
        id=util.get_request_uuid(),
        timestamp=request_timestamp,
        results=list(scrub_results)
    )
    current_app.logger.info("...Scrubb[ed]!")

    return response
