#!/usr/bin/env python3

import connexion

from cape_of_good_place_names import encoder


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Cape of Good Place Names Service'}, pythonic_params=True)
    app.run(port=8000)


if __name__ == '__main__':
    main()
