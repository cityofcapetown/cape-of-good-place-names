import datetime
import functools
import hashlib
from json.decoder import JSONDecodeError
import os
import pprint

from flask import current_app, request, has_request_context, json
import pytz
import six
import typing

from cape_of_good_place_names.config import config


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif type(klass) == typing.GenericMeta:
        if klass.__extra__ == list:
            return _deserialize_list(data, klass.__args__[0])
        if klass.__extra__ == dict:
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return a original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        if data is not None \
                and instance.attribute_map[attr] in data \
                and isinstance(data, (list, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type)
            for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type)
            for k, v in six.iteritems(data)}


def get_request_uuid():
    request_id = 'NA'
    if has_request_context():
        request_id = request.environ.get("HTTP_X_REQUEST_ID")

    return request_id


def get_timestamp():
    tz = pytz.timezone(current_app.config["TIMEZONE"])
    return datetime.datetime.now(tz=tz)


@functools.lru_cache(1)
def secure_mode(flush_cache=False):
    current_app.logger.debug("Checking auth status...")

    user_secrets_file_exists = os.path.exists(current_app.config["USER_SECRETS_FILE"])
    user_secrets_salt_exists = current_app.config["USER_SECRETS_SALT_KEY"] in get_secrets()

    current_app.logger.debug(f"user_secrets_file_exists={user_secrets_file_exists} and "
                             f"user_secrets_salt_exists={user_secrets_salt_exists}")
    return user_secrets_file_exists and user_secrets_salt_exists


def _config_spec_instantiator(config_spec):
    for klass, klass_params_lookup_dict in config_spec:
        current_app.logger.debug(f"Attempting to configure '{klass.__name__}'...")
        klass_params = {}

        skip_flag = False
        if len(klass_params_lookup_dict):
            for param, (lookup_namespace, *lookup_path) in klass_params_lookup_dict.items():
                current_app.logger.debug(f"Setting param '{param}' to '{lookup_namespace}':{'/'.join(lookup_path)}")
                assert isinstance(lookup_namespace, config.ConfigNamespace), (
                    f"'{lookup_namespace}' is not a valid config namespace!"
                )
                # Setting the root of the lookup path
                if lookup_namespace is config.ConfigNamespace.CONFIG:
                    lookup_value = current_app.config
                else:
                    lookup_value = get_secrets() if secure_mode() else {}

                # Traversing the keys
                skip_flag = False
                for value in lookup_path:
                    if value not in lookup_value:
                        current_app.logger.error(f"'{value}' ('{'/'.join(lookup_path)}') not present!")
                        skip_flag = True
                        break
                    lookup_value = lookup_value[value]

                if skip_flag:
                    current_app.logger.warning(f"Couldn't set '{param}'!")
                    break

                current_app.logger.debug(
                    f"Value is {lookup_value if lookup_namespace is not config.ConfigNamespace.SECRETS else '<REDACTED>'}"
                )
                klass_params[param] = lookup_value

        if skip_flag:
            current_app.logger.warning(f"Skipping '{klass.__name__}'!")
            continue

        # Finally, configuring the object with the values that were looked up
        current_app.logger.debug(f"Configuring '{klass.__name__}' with '{', '.join(map(str, klass_params.keys()))}'")

        try:
            instantiated_obj = klass(**klass_params)
            yield instantiated_obj
        except Exception as e:
            current_app.logger.warning(f"Skipping '{klass.__name__}' because '{e.__class__.__name__}: {e}")


@functools.lru_cache(1)
def get_geocoders(flush_cache=False):
    current_app.logger.debug("Getting geocoders...")

    geocoders_config = current_app.config["GEOCODERS"]
    geocoders = list(_config_spec_instantiator(geocoders_config))

    assert len(geocoders) >= current_app.config["GEOCODERS_MIN"], "Less than the expected number of GEOCODERS"

    return geocoders


@functools.lru_cache(1)
def get_scrubbers(flush_cache=False):
    current_app.logger.debug("Getting scrubbers...")

    scrubber_config = current_app.config["SCRUBBERS"]
    scrubbers = list(_config_spec_instantiator(scrubber_config))

    assert len(scrubbers) >= current_app.config["SCRUBBERS_MIN"], "Less than the expected number of SCRUBBERS"

    return scrubbers


@functools.lru_cache(1)
def get_secrets(flush_cache=False):
    current_app.logger.info("Loading secrets...")

    if "SECRETS_FILE" in current_app.config:
        secrets_path = current_app.config["SECRETS_FILE"]
        current_app.logger.debug(f"SECRETS_FILE='{secrets_path}'")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path) as secrets_file:
                    return json.load(secrets_file)
            except JSONDecodeError as e:
                current_app.logger.error(f"JSON Decode failed! {e.__class__}: {e}")
        else:
            current_app.logger.warning(f"'{secrets_path}' does not exist!")

            # Walking the directory structure to the path
            debug_full_path = os.path.normpath(secrets_path)
            debug_secrets_path, _ = os.path.split(debug_full_path)
            debug_secrets_path_components = debug_secrets_path.split(os.sep)
            for i, _ in enumerate(debug_secrets_path_components):
                list_path = os.path.join(*map(lambda comp: os.sep + comp, debug_secrets_path_components[:i+1]))
                if os.path.exists(list_path):
                    current_app.logger.debug(f"os.listdir('{list_path}')='{pprint.pformat(os.listdir(list_path))}'")
                else:
                    current_app.logger.debug(f"'{list_path}' doesn't exist")
    else:
        current_app.logger.warning("'SECRETS_FILE' variable not defined!")

    current_app.logger.warning("No secrets found! Secrets object is empty.")
    return {}


@functools.lru_cache(1)
def get_user_secrets(flush_cache=False):
    current_app.logger.info("Loading user secrets...")

    if secure_mode():
        secrets_path = current_app.config["USER_SECRETS_FILE"]
        current_app.logger.debug(f"USER_SECRETS_FILE='{secrets_path}'")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path) as secrets_file:
                    return json.load(secrets_file)
            except JSONDecodeError as e:
                current_app.logger.error(f"JSON Decode failed! {e.__class__}: {e}")
        else:
            current_app.logger.warning(f"'{secrets_path}' does not exist!")
    else:
        current_app.logger.warning("Not running in secure mode!")

    current_app.logger.warning("No user secrets found! User Secrets object is empty.")
    return {}


@functools.lru_cache()
def auth_user(username, password):
    current_app.logger.info(f"Authing user '{username}'...")

    salt_key = current_app.config["USER_SECRETS_SALT_KEY"]
    secrets = get_secrets()
    user_secrets_salt = secrets[salt_key]
    user_secrets = get_user_secrets()

    # Curried hashing function
    def user_secret_hash(secret_value):
        return hashlib.sha256(
            (secret_value + user_secrets_salt).encode()
        ).hexdigest()

    hashed_username = user_secret_hash(username)
    hashed_password = user_secret_hash(password)

    password_lookup = user_secrets.get(hashed_username, None)
    current_app.logger.warning(f"User '{username}' doesn't exist!") if password_lookup is None else None
    password_check = password_lookup == hashed_password
    current_app.logger.warning(f"Password for user '{username}' is {'correct' if password_check else 'incorrect'}")

    return password_check


def flush_caches():
    current_app.logger.info("Flushing caches!")
    get_secrets(flush_cache=True)
    get_user_secrets(flush_cache=True)
    secure_mode(flush_cache=True)
    get_geocoders(flush_cache=True)
    get_scrubbers(flush_cache=True)

    get_secrets(flush_cache=False)
    get_user_secrets(flush_cache=False)
    secure_mode(flush_cache=False)
    get_geocoders(flush_cache=False)
    get_scrubbers(flush_cache=False)
