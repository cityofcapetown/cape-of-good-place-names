from connexion.exceptions import Unauthorized
from flask import current_app

from cape_of_good_place_names import util

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
def check_basicAuth(username, password, required_scopes):
    current_app.logger.debug(f"Checking '{username}'...")
    secure_mode = util.secure_mode(flush_cache=False)

    if secure_mode:
        user_auth_check = util.auth_user(username, password)
        current_app.logger.debug(f"user_auth_check='{user_auth_check}'")
        if user_auth_check:
            return {}
        else:
            raise Unauthorized("Sorry - username or password is incorrect!")
    else:
        current_app.logger.warning(f"Passing through '{username}' because I'm not in secure mode!")
        return {}
