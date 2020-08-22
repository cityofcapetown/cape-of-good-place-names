import datetime
import functools
from json.decoder import JSONDecodeError
import os

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
def get_geocoders(flush_cache=False):
    current_app.logger.debug("Getting geocoders...")
    default_geocoders = current_app.config["DEFAULT_GEOCODERS"]
    geocoders = [
        gc()
        for gc in default_geocoders
    ]

    configurable_geocoders = current_app.config["CONFIGURABLE_GEOCODERS"]
    for gc, gc_params_lookup_dict in configurable_geocoders:
        current_app.logger.debug(f"Attempting to configure '{gc.__name__}'...")
        gc_params = {}
        skip_flag = True
        for param, (lookup_namespace, *lookup_path) in gc_params_lookup_dict.items():
            current_app.logger.debug(f"Setting param '{param}' to '{lookup_namespace}':{'/'.join(lookup_path)}")
            assert isinstance(lookup_namespace, config.ConfigNamespace), (
                    f"'{lookup_namespace}' is not a valid config namespace!"
            )
            # Setting the root of the lookup path
            if lookup_namespace is config.ConfigNamespace.CONFIG:
                lookup_value = current_app.config
            else:
                lookup_value = get_secrets()

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
            gc_params[param] = lookup_value

        if skip_flag:
            current_app.logger.warning(f"Skipping '{gc.__name__}'!")
            continue

        # Finally, configuring the geocoder with the values that were looked up
        current_app.logger.debug(f"Configuring '{gc.__name__}' with '{', '.join(map(str, gc_params.keys()))}'")
        geocoders += [gc(**gc_params)]

    return geocoders


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
    else:
        current_app.logger.warning("'SECRETS_FILE' variable not defined!")

    current_app.logger.warning("No secrets found! Secrets object is empty.")
    return {}
