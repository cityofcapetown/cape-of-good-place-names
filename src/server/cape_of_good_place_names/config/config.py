import enum

from geocode_array import Nominatim, CCT, ArcGIS, Google
from basic_scrubber import BasicScrubber


class ConfigNamespace(enum.Enum):
    CONFIG = "config"
    SECRETS = "secrets"


class Config(object):
    # High level config
    TIMEZONE = "Africa/Johannesburg"
    REQUEST_ID_UNIQUE_VALUE_PREFIX = "cogpn-"
    SECRETS_FILE = "/data/secrets/secrets.json"

    # GeoLookup config
    GEOLOOKUP_DATASET_DIR = "/data/lookup_layers"
    GEOLOOKUP_DATASET_CONFIG = {
        # Layer ID: (Layer filename, Property ID attribute)
    }

    # Geocoder config
    DEFAULT_GEOCODERS = [Nominatim.Nominatim, CCT.CCT, ArcGIS.ArcGIS, ]
    CONFIGURABLE_GEOCODERS = (
        # ( Geocoder Class: { keyword arg name: [<namespace>, key1, key2, key3] )
        # namespaces currently supported: secrets, config
        (
            Google.Google, {"api_key": [ConfigNamespace.SECRETS, "google", "maps-api-key"]}
        ),
    )

    # Scrub config
    SCRUBBERS = [BasicScrubber.BasicScrubber]
