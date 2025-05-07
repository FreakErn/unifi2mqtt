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
    --mqtt-host "mqtt.local" \
    --unifi-user "localUser" \
    --unifi-pass "localUserPass" \
    --mqtt-topic Unifi2Mqtt \
    --unifi-ignore-ssl \
    --filter-macs aa:bb:cc:dd:ee:ff,11:22:33:44:55:66
```
