import json
import logging
import time

import paho.mqtt.client as mqtt
import requests
from urllib3.exceptions import InsecureRequestWarning

from .lib.app_settings import settings
from .lib.client import load_persisted_clients, save_connected_clients, get_last_seen_for_client
from .lib.unifi import fetch_clients, is_connected, site_exists
from .lib.utils import timestamp_to_isoformat

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def run_monitor():
    mqtt_client = mqtt.Client(client_id=settings.mqtt_client_id, protocol=mqtt.MQTTv5)
    if settings.mqtt_user and settings.mqtt_pass:
        mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
    mqtt_client.connect(settings.mqtt_host, settings.mqtt_port)
    mqtt_client.loop_start()

    if mqtt_client.is_connected():
        logger.info(f"Successfully connected to {settings.mqtt_host}")

    session = requests.Session()
    if settings.unifi_ignore_ssl:
        session.verify = False
    logger.debug("ssl verification: " + str(not settings.unifi_ignore_ssl))

    auth_payload = {
        "username": settings.unifi_user,
        "password": settings.unifi_pass
    }
    logger.info(f"Login as {auth_payload['username']}")

    filter_macs = set(mac.strip().lower() for mac in settings.filter_macs.split(",")) if settings.filter_macs else None
    connected_clients = {}

    # load clients which were connected on previous run
    last_state = load_persisted_clients()
    logger.debug(f"Loaded {len(last_state)} previous saved, connected clients.")

    if not site_exists(session, settings.unifi_url, auth_payload, settings.unifi_ignore_ssl, settings.unifi_site):
        logger.error(f"Site '{settings.unifi_site}' does not exist. Please check your settings.")
        return

    try:
        while True:
            try:

                clients = fetch_clients(session, settings.unifi_url, auth_payload, settings.unifi_ignore_ssl,
                                        settings.unifi_site)

                current_macs = set()
                for client in clients:
                    mac = client.get("mac", "").lower()
                    if filter_macs and mac not in filter_macs:
                        continue
                    if not is_connected(client, settings.timeout):
                        continue
                    current_macs.add(mac)
                    connected_clients[mac] = client
                    name = client.get("name") or client.get("hostname") or mac
                    msg = json.dumps({
                        "event": "connected",
                        "mac": mac,
                        "name": name,
                        "last_uplink_name": client.get("last_uplink_name"),
                        "ip": client.get("ip"),
                        "online": True,
                        "last_seen": timestamp_to_isoformat(get_last_seen_for_client(client))
                    })

                    topic = f"{settings.mqtt_topic}/{mac.replace(':', '')}"
                    mqtt_client.publish(topic, payload=msg, qos=1, retain=True)
                    logger.info(f"Published online: {msg}")

                # Detect disconnected
                for mac in last_state:
                    if mac not in current_macs:
                        last_seen = get_last_seen_for_client(
                            connected_clients[mac]) if mac in connected_clients else "unknown"
                        msg = json.dumps({
                            "event": "disconnected",
                            "mac": mac,
                            "name": last_state[mac],
                            "online": False,
                            "last_seen": timestamp_to_isoformat(last_seen)
                        })
                        topic = f"{settings.mqtt_topic}/{mac.replace(':', '')}"
                        mqtt_client.publish(topic, payload=msg, qos=1, retain=True)
                        logger.info(f"Published offline: {msg}")

                # Update state
                last_state = {client["mac"].lower(): client.get("name") or client.get("hostname") or client["mac"]
                              for client in clients if not filter_macs or client["mac"].lower() in filter_macs}

                # Save the clients in case the application ends
                save_connected_clients(last_state)

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Exception: {e}")

            time.sleep(settings.interval)
    except KeyboardInterrupt:
        logger.info("unifi2mqtt stopped by user (Strg+C)")
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
