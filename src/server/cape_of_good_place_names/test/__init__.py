import logging
from logging.config import dictConfig

import connexion
from flask_testing import TestCase

from cape_of_good_place_names.encoder import JSONEncoder


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = JSONEncoder
        app.add_api('swagger.yaml')

        # Setting up custom logging
        root = logging.getLogger()
        formatter = logging.Formatter(
            '[%(asctime)s]-[PID:%(process)d]] %(module)s.%(funcName)s [%(levelname)s]: %(message)s',
            datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
        for handler in root.handlers:
            handler.setFormatter(formatter)

        return app.app
