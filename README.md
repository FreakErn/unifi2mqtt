# unifi2mqtt

Monitor Unifi clients and publish their connection status to an MQTT broker.

## Installation

```bash
pip install unifi2mqtt
```

## Usage

```bash
usage: unifi2mqtt [-h] --unifi-url UNIFI_URL --unifi-user UNIFI_USER --unifi-pass UNIFI_PASS [--unifi-ignore-ssl]
                  --mqtt-host MQTT_HOST [--mqtt-port MQTT_PORT] [--mqtt-user MQTT_USER] [--mqtt-pass MQTT_PASS]
                  [--mqtt-topic MQTT_TOPIC] [--mqtt-client-id MQTT_CLIENT_ID] [--timeout TIMEOUT]
                  [--filter-macs FILTER_MACS] [-i INTERVAL] [-d] [-v]

Monitor Unifi clients and publish status to MQTT

options:
  -h, --help                        show this help message and exit
  --unifi-url UNIFI_URL             URL of the Unifi Controller (default: None)
  --unifi-user UNIFI_USER           Unifi username (default: None)
  --unifi-pass UNIFI_PASS           Unifi password (default: None)
  --unifi-ignore-ssl                Ignore SSL verification (env variable UNIFI_IGNORE_SSL) (default: False)
  --mqtt-host MQTT_HOST             MQTT broker host (default: None)
  --mqtt-port MQTT_PORT             MQTT broker port (default: 1883)
  --mqtt-user MQTT_USER             MQTT username (default: None)
  --mqtt-pass MQTT_PASS             MQTT password (default: None)
  --mqtt-topic MQTT_TOPIC           MQTT topic prefix (default: unifi2mqtt)
  --mqtt-client-id MQTT_CLIENT_ID   MQTT client ID (default: unifi2mqtt)
  --timeout TIMEOUT                 Timeout in seconds for last_seen (Standard: 60) (default: 60)
  --filter-macs FILTER_MACS         Comma-separated list of MAC addresses to includeIf not set, you`ll get all clients
                                    listed (default: )
  -i INTERVAL, --interval INTERVAL  Interval in seconds between checks (default: 60)
  -d, --debug                       Enable debug logging (default: False)
  -v, --verbose                     Enable verbose logging (default: False)
  ```

## Launching it
You will need a local user for the programm to been able to run.
So go to `Settings` -> `Admin & Users` -> `Admins` -> `Create new User` and create a user and tick the "Restrict to Local Access Only". The User only needs `View Only` permissions.

### Running it locally
```bash
unifi2mqtt --interval 1 \
    --unifi-url "https://192.168.2.1" \
    --unifi-user "localUser" \
    --unifi-pass "localUserPass" \
    --mqtt-host "mqtt.local" \
    --unifi-ignore-ssl \ # if needed
    --filter-macs aa:bb:cc:dd:ee:ff,11:22:33:44:55:66
```

### Running it in Docker
```bash
docker run --d --restart=unless-stopped --name unifi2mqtt \
    -e UNIFI_URL=https://192.168.2.1 \
    -e UNIFI_USERNAME=localUser \
    -e UNIFI_PASSWORD=localUserPass \
    -e MQTT_HOST=mqtt.local \
    -e UNIFI_IGNORE_SSL=true \
    -e MQTT_TOPIC=unifi2mqtt \
    -e TZ=Europe/Berlin \
    -e FILTER_MACS=aa:bb:cc:dd:ee:ff,11:22:33:44:55:66
```
