# unifi2mqtt

Monitor Unifi clients and publish their connection status to an MQTT broker.

## Installation

```bash
pip install unifi2mqtt
```

## Usage

```bash
unifi2mqtt --interval 1 \
    --unifi-url "https://192.168.1.1" \
    --unifi-user "localUser" \
    --unifi-pass "localUserPass" \
    --mqtt-host "mqtt.local" \
    --mqtt-topic unifi2mqtt \
    --unifi-ignore-ssl \
    --filter-macs aa:bb:cc:dd:ee:ff,11:22:33:44:55:66
```


```bash
docker run --d --restart=unless-stopped --name unifi2mqtt \
    -e UNIFI_URL=https://192.168.1.1 \
    -e UNIFI_USERNAME=localUser \
    -e UNIFI_PASSWORD=localUserPass \
    -e MQTT_HOST=mqtt.local \
    -e UNIFI_IGNORE_SSL=true \
    -e MQTT_TOPIC=unifi2mqtt \
    -e FILTER_MACS=aa:bb:cc:dd:ee:ff,11:22:33:44:55:66
```
