from geocode_array import Nominatim, CCT, ArcGIS

TIMEZONE = "Africa/Johannesburg"
REQUEST_ID_UNIQUE_VALUE_PREFIX = "cogpn-"
GEOCODERS = [Nominatim.Nominatim, CCT.CCT, ArcGIS.ArcGIS,]

GEOLOOKUP_DATASET_DIR = "/data/lookup_layers"
GEOLOOKUP_DATASET_CONFIG = {
    # Layer ID: (Layer filename, Property ID attribute)
}