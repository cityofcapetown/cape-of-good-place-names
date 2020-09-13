import logging
import re

WHITESPACE_REGEX = re.compile(r'\W+')
DUNNING_KRUGER_CONFIDENCE = 1


class BasicScrubber:
    DEFAULT_INJECTION_VALUES = ["Western Cape", "South Africa"]

    def __init__(self, injection_values=None):
        self.injection_values = injection_values if injection_values else self.DEFAULT_INJECTION_VALUES

    def scrub(self, address):
        logging.debug(f"Received address '{address}'")
        new_address = address[:].strip()
        logging.debug(f"address after strip: '{new_address}'")

        for value in self.injection_values:
            if WHITESPACE_REGEX.sub("", value).lower() not in WHITESPACE_REGEX.sub("", new_address).lower():
                new_address = f"{new_address}, {value}"

        logging.debug(f"address after value injection: {new_address}")

        return new_address, DUNNING_KRUGER_CONFIDENCE
