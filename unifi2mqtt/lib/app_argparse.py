import argparse
import logging
import os

from unifi2mqtt.lib import app_constants
from unifi2mqtt.lib.app_settings import settings
from unifi2mqtt.lib.utils import str_to_bool


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs['max_help_position'] = 38  # Standard ist 24
        kwargs['width'] = 120  # Breite der gesamten Ausgabe
        super().__init__(*args, **kwargs)


def parse_args():
    parser = argparse.ArgumentParser(description="Monitor Unifi clients and publish status to MQTT",
                                     formatter_class=CustomFormatter)

    def env_or_default(env, default=None):
        return os.environ.get(env, default)

    parser.add_argument("--unifi-url", required=not bool(env_or_default("UNIFI_URL")),
                        default=env_or_default("UNIFI_URL"), help="URL of the Unifi Controller")
    parser.add_argument("--unifi-user", required=not bool(env_or_default("UNIFI_USER")),
                        default=env_or_default("UNIFI_USER"), help="Unifi username")
    parser.add_argument("--unifi-pass", required=not bool(env_or_default("UNIFI_PASS")),
                        default=env_or_default("UNIFI_PASS"), help="Unifi password")
    parser.add_argument("--unifi-site", default=env_or_default("UNIFI_SITE", "default"),
                        help="Unifi site")

    parser.add_argument("--unifi-ignore-ssl", action="store_true",
                        help="Ignore SSL verification (env variable UNIFI_IGNORE_SSL)")  # env var: UNIFI_IGNORE_SSL

    parser.add_argument("--mqtt-host", required=not bool(env_or_default("MQTT_HOST")),
                        default=env_or_default("MQTT_HOST"), help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=int(env_or_default("MQTT_PORT", 1883)),
                        help="MQTT broker port")
    parser.add_argument("--mqtt-user", default=env_or_default("MQTT_USER"), help="MQTT username")
    parser.add_argument("--mqtt-pass", default=env_or_default("MQTT_PASS"), help="MQTT password")
    parser.add_argument("--mqtt-topic", default=env_or_default("MQTT_TOPIC", "unifi2mqtt"),
                        help="MQTT topic prefix")
    parser.add_argument("--mqtt-client-id", default=env_or_default("MQTT_CLIENT_ID", "unifi2mqtt"),
                        help="MQTT client ID")
    parser.add_argument("--timeout", type=int, default=env_or_default("TIMEOUT", 60),
                        help="Timeout in seconds for last_seen (Standard: 60)")

    parser.add_argument("--filter-macs", default=env_or_default("FILTER_MACS", ""),
                        help="Comma-separated list of MAC addresses to include. If not set, you'll get all clients listed")
    parser.add_argument("-i", "--interval", type=int, default=int(env_or_default("INTERVAL", 60)),
                        help="Interval in seconds between checks")
    parser.add_argument("--use-specific-last-seen", default=env_or_default("USE_SPECIFIC_LAST_SEEN", None),
                        choices=app_constants.LAST_SEEN_FIELDS,
                        help="Comma-separated list of MAC addresses to includeIf not set, you'll get all clients listed")

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if not args.unifi_ignore_ssl:
        args.unifi_ignore_ssl = str_to_bool(os.getenv("UNIFI_IGNORE_SSL", "false"))

    # configure logging
    log_level = logging.ERROR
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    # fill settings
    settings.unifi_url = args.unifi_url
    settings.unifi_user = args.unifi_user
    settings.unifi_pass = args.unifi_pass
    settings.unifi_site = args.unifi_site
    settings.unifi_ignore_ssl = args.unifi_ignore_ssl

    settings.mqtt_host = args.mqtt_host
    settings.mqtt_port = args.mqtt_port
    settings.mqtt_user = args.mqtt_user
    settings.mqtt_pass = args.mqtt_pass
    settings.mqtt_topic = args.mqtt_topic
    settings.mqtt_client_id = args.mqtt_client_id

    settings.timeout = int(args.timeout)
    settings.filter_macs = args.filter_macs or ""
    settings.interval = int(args.interval)
    settings.use_specific_last_seen = args.use_specific_last_seen or None

    settings.debug = bool(args.debug)
    settings.verbose = bool(args.verbose)

    return args
