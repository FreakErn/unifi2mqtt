import argparse
import os
import logging

def parse_args():
    parser = argparse.ArgumentParser(description="Monitor Unifi clients and publish status to MQTT")

    def env_or_default(env, default=None):
        return os.environ.get(env, default)

    parser.add_argument("--unifi-url", required=not bool(env_or_default("UNIFI_URL")),
                        default=env_or_default("UNIFI_URL"), help="URL of the Unifi Controller")
    parser.add_argument("--unifi-user", required=not bool(env_or_default("UNIFI_USER")),
                        default=env_or_default("UNIFI_USER"), help="Unifi username")
    parser.add_argument("--unifi-pass", required=not bool(env_or_default("UNIFI_PASS")),
                        default=env_or_default("UNIFI_PASS"), help="Unifi password")
    parser.add_argument("--unifi-ignore-ssl", action="store_true", help="Ignore SSL verification")

    parser.add_argument("--mqtt-host", required=not bool(env_or_default("MQTT_HOST")),
                        default=env_or_default("MQTT_HOST"), help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=int(env_or_default("MQTT_PORT", 1883)), help="MQTT broker port")
    parser.add_argument("--mqtt-user", default=env_or_default("MQTT_USER"), help="MQTT username")
    parser.add_argument("--mqtt-pass", default=env_or_default("MQTT_PASS"), help="MQTT password")
    parser.add_argument("--mqtt-topic", default=env_or_default("MQTT_TOPIC", "unifi2mqtt"), help="MQTT topic prefix")
    parser.add_argument("--mqtt-client-id", default=env_or_default("MQTT_CLIENT_ID", "unifi2mqtt"), help="MQTT client ID")

    parser.add_argument("--filter-macs", default=env_or_default("FILTER_MACS", ""), help="Comma-separated list of MAC addresses to include")
    parser.add_argument("-i", "--interval", type=int, default=int(env_or_default("INTERVAL", 1)), help="Interval in minutes between checks")

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    log_level = logging.ERROR
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    return args