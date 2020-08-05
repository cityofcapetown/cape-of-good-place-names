import logging

import connexion
from flask_testing import TestCase

from cape_of_good_place_names.encoder import JSONEncoder


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = JSONEncoder
        app.add_api('swagger.yaml')

        app.app.config["TIMEZONE"] = "Africa/Johannesburg"

        return app.app
