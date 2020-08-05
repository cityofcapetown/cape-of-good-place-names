#!/usr/bin/env python3

import logging

import connexion
from flask import request, has_request_context
from flask.logging import default_handler
from flask_request_id_header.middleware import RequestID

from cape_of_good_place_names import encoder


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_id = 'NA'

        if has_request_context():
            record.request_id = request.environ.get("HTTP_X_REQUEST_ID")

        return super().format(record)


def main():
    # Creating swagger-based app
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Cape of Good Place Names Service'}, pythonic_params=True)

    # Setting up configuration
    app.app.config.from_object("cape_of_good_place_names")

    # Setting up request ID
    RequestID(app.app)
    formatter = RequestFormatter(
        '[%(asctime)s] [%(levelname)s] [%(request_id)s] %(module)s: %(message)s'
    )
    default_handler.setFormatter(formatter)

    # Running!
    app.run(port=8000, debug=True)


if __name__ == '__main__':
    main()
