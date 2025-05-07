import time
import logging
import requests
import paho.mqtt.client as mqtt
from urllib3.exceptions import InsecureRequestWarning

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def run_monitor(args):
    mqtt_client = mqtt.Client(client_id=args.mqtt_client_id, protocol=mqtt.MQTTv5)
    if args.mqtt_user and args.mqtt_pass:
        mqtt_client.username_pw_set(args.mqtt_user, args.mqtt_pass)
    mqtt_client.connect(args.mqtt_host, args.mqtt_port)
    mqtt_client.loop_start()

    session = requests.Session()
    if args.unifi_ignore_ssl:
        session.verify = False

    auth_payload = {
        "username": args.unifi_user,
        "password": args.unifi_pass
    }

    filter_macs = set(mac.strip().lower() for mac in args.filter_macs.split(",")) if args.filter_macs else None
    last_state = {}

    try:
        while True:
            try:
                logger.debug("Authenticating with UniFi Controller...")
                session.post(f"{args.unifi_url}/api/auth/login", json=auth_payload)
                
                for cookie in session.cookies:
                    logging.debug(f"Cookie: {cookie.name} = {cookie.value}")

                logger.debug("Fetching client list...")
                resp = session.get(f"{args.unifi_url}/proxy/network/api/s/default/stat/sta")
                resp.raise_for_status()
                clients = resp.json()["data"]

                current_macs = set()
                for client in clients:
                    mac = client.get("mac", "").lower()
                    if filter_macs and mac not in filter_macs:
                        continue
                    current_macs.add(mac)
                    name = client.get("name") or client.get("hostname") or mac
                    online = True
                    msg = {
                        "mac": mac,
                        "name": name,
                        "ip": client.get("ip"),
                        "online": online
                    }

                    topic = f"{args.mqtt_topic}/{mac.replace(':', '')}"
                    mqtt_client.publish(topic, payload=str(msg), qos=1, retain=True)
                    logger.debug(f"Published online: {msg}")

                # Detect disconnected
                for mac in last_state:
                    if mac not in current_macs:
                        msg = {
                            "mac": mac,
                            "name": last_state[mac],
                            "online": False
                        }
                        topic = f"{args.mqtt_topic}/{mac.replace(':', '')}"
                        mqtt_client.publish(topic, payload=str(msg), qos=1, retain=True)
                        logger.debug(f"Published offline: {msg}")

                # Update state
                last_state = {client["mac"].lower(): client.get("name") or client.get("hostname") or client["mac"]
                              for client in clients if not filter_macs or client["mac"].lower() in filter_macs}

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Exception: {e}")

            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        logger.info("Beendet durch Benutzer (Strg+C)")
        mqtt_client.disconnect()
        mqtt_client.loop_stop()