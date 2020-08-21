from geocode_array import Nominatim, CCT, ArcGIS
from basic_scrubber import BasicScrubber


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
    DEFAULT_GEOCODERS = [Nominatim.Nominatim, CCT.CCT, ArcGIS.ArcGIS,]

    # Scrub config
    SCRUBBERS = [BasicScrubber.BasicScrubber]

