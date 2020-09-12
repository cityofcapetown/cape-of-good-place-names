import enum

from geocode_array import Nominatim, CCT, ArcGIS, Google
from basic_scrubber import BasicScrubber
from phdc_scrubber import PhdcScrubber


class ConfigNamespace(enum.Enum):
    CONFIG = "config"
    SECRETS = "secrets"


class Config(object):
    # High level config
    TIMEZONE = "Africa/Johannesburg"
    REQUEST_ID_UNIQUE_VALUE_PREFIX = "cogpn-"

    # Secrets config
    SECRETS_FILE = "/data/secrets/secrets.json"

    USER_SECRETS_SALT_KEY = "cogpn-user-salt"
    USER_SECRETS_FILE = "/data/secrets/user-secrets.json"

    # GeoLookup config
    GEOLOOKUP_DATASET_DIR = "/data/lookup_layers"
    GEOLOOKUP_DATASET_CONFIG = {
        # Layer ID: (Layer filename, Property ID attribute)
    }

    # Geocoder config
    GEOCODERS = (
        # ( Geocoder Class: { keyword arg name: [<namespace>, key1, key2, key3] )
        # namespaces currently supported: secrets, config
        (
            Nominatim.Nominatim, {}
        ),
        (
            CCT.CCT, {}
        ),
        (
            ArcGIS.ArcGIS, {}
        ),
        (
            Google.Google, {"api_key": [ConfigNamespace.SECRETS, "google", "maps-api-key"]}
        ),
    )
    GEOCODERS_MIN = 3

    # Scrub config
    SCRUBBER_DATASET_DIR = "/data/scrubber_data"
    SCRUBBERS = (
        # ( Scrubber Class: { keyword arg name: [<namespace>, key1, key2, key3] )
        # namespaces currently supported: secrets, config
        (
            BasicScrubber.BasicScrubber, {}
        ),
        (
            PhdcScrubber.PhdcScrubber, {"datadir": [ConfigNamespace.CONFIG, "SCRUBBER_DATASET_DIR"]}
        ),
    )
    SCRUBBERS_MIN = 1
