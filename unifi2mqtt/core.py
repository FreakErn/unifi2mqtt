import datetime
import json
import logging
import os
import requests
import paho.mqtt.client as mqtt
import time
from urllib3.exceptions import InsecureRequestWarning

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

PERSIST_FILE = "connected_clients.json"

def load_persisted_clients():
    if os.path.exists(PERSIST_FILE):
        with open(PERSIST_FILE, "r") as f:
            return json.load(f)
    return {}

def save_connected_clients(mac_set):
    with open(PERSIST_FILE, "w") as f:
        json.dump(mac_set, f)

def is_connected(client, timeout):
    now = time.time()
    last_seen = client.get("last_seen", 0)
    return (now - last_seen) <= timeout

def timestamp_to_isoformat(timestamp):
    if timestamp is None:
        return None
    try:
        dt = datetime.datetime.fromtimestamp(float(timestamp))
        return dt.isoformat()
    except (ValueError, OSError, TypeError):
        return None

def login(session, url: str, login_payload: dict, ignore_ssl: bool):
    login_url = f"{url.rstrip('/')}/api/auth/login"
    logger.debug(f"Logging in to {login_url}")
    response = session.post(
        login_url,
        json={
            "username": login_payload["username"],
            "password": login_payload["password"]
        },
        verify=not ignore_ssl
    )
    response.raise_for_status()
    logger.info("Successfully logged in.")

def fetch_clients(session, url: str, login_payload: dict, ignore_ssl: bool):
    return _request_with_reauth(session, url, login_payload, ignore_ssl, _get_clients)

def _get_clients(session, url: str, login_payload: dict, ignore_ssl: bool):
    clients_url = f"{url.rstrip('/')}/proxy/network/api/s/default/stat/sta"
    logger.debug(f"Fetching clients from {clients_url}")
    response = session.get(clients_url, verify=not ignore_ssl)
    response.raise_for_status()
    return response.json().get("data", [])

def _request_with_reauth(session, url: str, login_payload: dict, ignore_ssl: bool, action):
    try:
        return action(session, url, login_payload, ignore_ssl)
    except requests.HTTPError as e:
        if 400 <= e.response.status_code < 500:
            logger.warning(f"HTTP {e.response.status_code} - retrying after login.")
            login(session, url, login_payload, ignore_ssl)
            return action(session, url, login_payload, ignore_ssl)
        raise

def run_monitor(args):
    mqtt_client = mqtt.Client(client_id=args.mqtt_client_id, protocol=mqtt.MQTTv5)
    if args.mqtt_user and args.mqtt_pass:
        mqtt_client.username_pw_set(args.mqtt_user, args.mqtt_pass)
    mqtt_client.connect(args.mqtt_host, args.mqtt_port)
    mqtt_client.loop_start()

    session = requests.Session()
    if args.unifi_ignore_ssl:
        session.verify = False
    logger.debug("ssl verification: " + str(not args.unifi_ignore_ssl))

    auth_payload = {
        "username": args.unifi_user,
        "password": args.unifi_pass
    }


    filter_macs = set(mac.strip().lower() for mac in args.filter_macs.split(",")) if args.filter_macs else None
    connected_clients = {}

    # load clients which were connected on previous run
    last_state = load_persisted_clients()
    logger.debug(f"Loaded {len(last_state)} persisted connected clients.")

    try:
        while True:
            try:

                clients = fetch_clients(session, args.unifi_url, auth_payload, args.unifi_ignore_ssl)
                client_seen_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

                current_macs = set()
                for client in clients:
                    mac = client.get("mac", "").lower()
                    if filter_macs and mac not in filter_macs:
                        continue
                    if not is_connected(client, args.timeout):
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
                        "last_seen": timestamp_to_isoformat(client.get("last_seen"))
                    })

                    topic = f"{args.mqtt_topic}/{mac.replace(':', '')}"
                    mqtt_client.publish(topic, payload=msg, qos=1, retain=True)
                    logger.debug(f"Published online: {msg}")


                # Detect disconnected
                for mac in last_state:
                    if mac not in current_macs:
                        msg = json.dumps({
                            "event": "disconnected",
                            "mac": mac,
                            "name": last_state[mac],
                            "online": False,
                            "last_seen": timestamp_to_isoformat(client.get("last_seen"))
                        })
                        topic = f"{args.mqtt_topic}/{mac.replace(':', '')}"
                        mqtt_client.publish(topic, payload=msg, qos=1, retain=True)
                        logger.debug(f"Published offline: {msg}")

                # Update state
                last_state = {client["mac"].lower(): client.get("name") or client.get("hostname") or client["mac"]
                              for client in clients if not filter_macs or client["mac"].lower() in filter_macs}
                
                # Save the clients in case the application ends
                save_connected_clients(last_state)

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Exception: {e}")

            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Beendet durch Benutzer (Strg+C)")
        mqtt_client.disconnect()
        mqtt_client.loop_stop()