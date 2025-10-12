# python
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    # Unifi
    unifi_url: str | None = None
    unifi_user: str | None = None
    unifi_pass: str | None = None
    unifi_site: str = "default"
    unifi_ignore_ssl: bool = False

    # MQTT
    mqtt_host: str | None = None
    mqtt_port: int = 1883
    mqtt_user: str | None = None
    mqtt_pass: str | None = None
    mqtt_topic: str = "unifi2mqtt"
    mqtt_client_id: str = "unifi2mqtt"

    # Verhalten
    timeout: int = 60
    filter_macs: str = ""
    interval: int = 60
    use_specific_last_seen: str = None

    # Logging
    debug: bool = False
    verbose: bool = False


settings = Settings()
