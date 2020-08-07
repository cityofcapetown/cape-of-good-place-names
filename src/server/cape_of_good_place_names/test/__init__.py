import logging

import connexion
from geocode_array.Geocoder import Geocoder
from flask_testing import TestCase

from cape_of_good_place_names.encoder import JSONEncoder


class MockGeocoder(Geocoder):
    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        return address_string, 0.0, 0.0, None


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = JSONEncoder
        app.add_api('swagger.yaml')

        app.app.config["TIMEZONE"] = "Africa/Johannesburg"

        return app.app
