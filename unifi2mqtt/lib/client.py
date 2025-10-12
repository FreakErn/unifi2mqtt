import json
import os
import logging

from unifi2mqtt.lib import app_constants
from unifi2mqtt.lib.app_settings import settings
from unifi2mqtt.lib.utils import timestamp_to_isoformat

logger = logging.getLogger(__name__)

def load_persisted_clients():
    if os.path.exists(app_constants.PERSIST_FILE):
        with open(app_constants.PERSIST_FILE, "r") as f:
            return json.load(f)
    return {}


def save_connected_clients(mac_set):
    with open(app_constants.PERSIST_FILE, "w") as f:
        json.dump(mac_set, f)


def get_last_seen_for_client(client):
    if settings.use_specific_last_seen is not None:
        if settings.verbose:
            logger.debug(f"VERBOSE: using specific last seen field: {settings.use_specific_last_seen}")
        return client.get(settings.use_specific_last_seen)

    # just some overengineered logging
    if settings.verbose:
        parts: list[str] = []
        for field in app_constants.LAST_SEEN_FIELDS:
            if field in client:
                value = client.get(field)
                if value is not None:
                    parts.append(f"{field}: {timestamp_to_isoformat(value)}")

        if parts:
            logger.debug("VERBOSE: " + ", ".join(parts))

    # now we search for the lastest unifi device/application which has seen our client
    best_timestamp_key, best_timestamp = get_best_timestamp(client)

    if settings.verbose:
        logger.debug(
            f"VERBOSE: best_timestamp_key: {best_timestamp_key}, best_timestamp: {best_timestamp} ({timestamp_to_isoformat(best_timestamp) if best_timestamp is not None else "unknown"})")

    return best_timestamp


def get_best_timestamp(client):
    best_timestamp_key, best_timestamp = max(
        ((k, int(client[k])) for k in app_constants.LAST_SEEN_FIELDS if client.get(k) is not None),
        key=lambda kv: kv[1],
        default=(None, None),
    )
    return best_timestamp_key, best_timestamp
