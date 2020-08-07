from geocode_array import Nominatim, CCT, ArcGIS
from basic_scrubber import BasicScrubber

TIMEZONE = "Africa/Johannesburg"
REQUEST_ID_UNIQUE_VALUE_PREFIX = "cogpn-"

# Geocoder config
GEOCODERS = [Nominatim.Nominatim, CCT.CCT, ArcGIS.ArcGIS,]

# GeoLookup config
GEOLOOKUP_DATASET_DIR = "/data/lookup_layers"
GEOLOOKUP_DATASET_CONFIG = {
    # Layer ID: (Layer filename, Property ID attribute)
}

# Scrub config
SCRUBBERS = [BasicScrubber.BasicScrubber]
