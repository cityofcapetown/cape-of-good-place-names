#!/usr/bin/env python3

import argparse
import logging

import cape_of_good_place_names_client as cogpn
from cape_of_good_place_names_client.api import default_api
import urllib3

# Config values
DEFAULT_SERVER = "https://api-dev.cape-of-good-place-names.xyz"
SCRUBBER = "PhdcScrubber"
GEOCODER = "CombinedGeocoders"


def setup_arg_parser():
    arg_parser = argparse.ArgumentParser(
        description="Utility script for processing an address using the Cape of Good Place Names service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument('-a', '--address', required=True,
                            help="""Address to process""")

    arg_parser.add_argument('-u', '--username', required=True,
                            help='Username to use for Cape of Good Place Name Service')

    arg_parser.add_argument('-p', '--password', required=True,
                            help='Password to use for Cape of Good Place Name Service')

    arg_parser.add_argument("-x", "--proxy", required=False, default=None,
                            help="Internet proxy address")

    arg_parser.add_argument("-xu", "--proxy-username", required=False, default=None,
                            help="Internet proxy username")

    arg_parser.add_argument("-xp", "--proxy-password", required=False, default=None,
                            help="Internet proxy password")

    arg_parser.add_argument('-s', '--server', required=False, default=DEFAULT_SERVER,
                            help='Cape of Good Place Name Service server name to use')

    arg_parser.add_argument('-sc', '--scrubber', required=False, default=SCRUBBER,
                            help='ID of scrubber result to use')

    arg_parser.add_argument('-gc', '--geocoder', required=False, default=GEOCODER,
                            help='ID of geocoder result to use')

    arg_parser.add_argument('-v', '--verbose', required=False, action='store_true',
                            help="""Verbosity flag""")

    arg_parser.add_argument('-o', '--output', required=False, default='/dev/stdout',
                            help="""Output file""")

    return arg_parser


def get_proxy_headers(proxy_username, proxy_password):
    proxy_headers = urllib3.util.make_headers(
        proxy_basic_auth=f"{proxy_username}:{proxy_password}"
    )
    return proxy_headers


if __name__ == "__main__":
    parser = setup_arg_parser()
    args, _ = parser.parse_known_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s-%(module)s [%(levelname)s]: %(message)s')

    # Configuring the service
    config = cogpn.Configuration()
    config.username = args.username
    config.password = args.password
    config.host = args.server

    # configuring the proxy
    if args.proxy:
        config.proxy = args.proxy
        if args.proxy_username and args.proxy_password:
            config.proxy_headers = get_proxy_headers(args.proxy_username, args.proxy_password)

    # Setting up the API client - this is inside a context manager that takes cares of underlying IO threads
    with cogpn.ApiClient(configuration=config) as api_client:
        cogpn_client = default_api.DefaultApi(api_client)

        # Performing the scrub operation
        logging.info("Scrub[ing]...")
        scrubbing_results = cogpn_client.scrub(args.address)
        logging.debug(f"scrubbing_results=\n{scrubbing_results}")

        # Selecting the result we want from the scrub results
        scrubbed_address = None
        for result in scrubbing_results.results:
            if result.scrubber_id == args.scrubber:
                scrubbed_address = result.scrubbed_value
        assert scrubbed_address, "Scrubbing failed!"
        logging.debug(f"scrubbed_address='{scrubbed_address}'")

        logging.info("...Scrub[ed]")

        # Performing the geocode operation
        logging.info("Geocod[ing]...")
        geocoding_results = cogpn_client.geocode(scrubbed_address)
        logging.debug(f"geocoding_results=\n{geocoding_results}")

        # Selecting the result we want from the geocode results
        geocoded_value = None
        for result in geocoding_results.results:
            if result.geocoder_id == args.geocoder:
                geocoded_value = result.geocoded_value
        assert scrubbed_address, "Geocoding failed!"
        logging.debug(f"geocoded_value=\n{geocoded_value}")
        logging.info("...Geocod[ed]")

        # Outputting result
        with open(args.output, "w") as output_file:
            output_file.write(geocoded_value)
