#!/usr/bin/env python3

import logging
from logging.config import dictConfig

import connexion
from flask import request, has_request_context
from flask_request_id_header.middleware import RequestID

from cape_of_good_place_names import encoder, util


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
    app.app.config.from_object("cape_of_good_place_names.config.config.Config")

    # Setting up request ID
    RequestID(app.app)

    # Setting up custom logging
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })

    root = logging.getLogger()
    formatter = RequestFormatter(
        '[%(asctime)s]-[PID:%(process)d]-[RID:%(request_id)s] %(module)s.%(funcName)s [%(levelname)s]: %(message)s',
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    for handler in root.handlers:
        handler.setFormatter(formatter)

    # Bootstrapping
    with app.app.app_context():
        # Secrets
        secrets = util.get_secrets()
        app.app.logger.info(f"Secrets' top-level keys: {', '.join(map(str,secrets.keys()))}")

        # Secure Mode
        app.app.logger.warning(f"Starting in {'*secure*' if util.secure_mode() else '*insecure*'} mode")

        # Geocoders
        geocoders = util.get_geocoders()
        geocoder_names = (
            gc.__class__.__name__
            for gc in geocoders
        )
        app.app.logger.info(f"Geocoders: {', '.join(geocoder_names)}")

        # Scrubbers
        scrubbers = util.get_scrubbers()
        scrubber_names = (
            sc.__class__.__name__
            for sc in scrubbers
        )
        app.app.logger.info(f"Scrubbers: {', '.join(scrubber_names)}")

    # Running!
    app.run(port=8000, debug=False)


if __name__ == '__main__':
    main()
