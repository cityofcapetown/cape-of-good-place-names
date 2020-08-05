from geocode_array import Nominatim, CCT, ArcGIS

TIMEZONE = "Africa/Johannesburg"
REQUEST_ID_UNIQUE_VALUE_PREFIX = "cogpn-"
GEOCODERS = [Nominatim.Nominatim, CCT.CCT, ArcGIS.ArcGIS,]