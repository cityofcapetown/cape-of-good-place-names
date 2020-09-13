#!/usr/bin/env python3

import argparse
import logging

from phdc_scrubber import PhdcScrubber

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s-%(module)s.%(funcName)s [%(levelname)s]: %(message)s')

    parser = argparse.ArgumentParser(
        description="Utility script for testing PHDC Scrubber"
    )

    parser.add_argument('-d', '--datadir', required=True,
                        help='Directory containing expected datafiles')

    parser.add_argument('-a', '--address', required=True,
                        help="""Address to scrub""")

    args, _ = parser.parse_known_args()
    datadir = args.datadir
    address = args.address

    logging.debug(f"{PhdcScrubber.STREET_NO_REGEX_PATTERN}")
    scrubber = PhdcScrubber.PhdcScrubber(datadir=datadir)
    scrubbed_address, scrubbed_confidence = scrubber.scrub(address)

    logging.info(f"Non-Scrubbed Address: '{address}'")
    logging.info(f"    Scrubbed Address: '{scrubbed_address}'")
    logging.info(f"          Confidence: '{scrubbed_confidence:.0%}'")

