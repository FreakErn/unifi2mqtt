import logging
import time

import requests

from unifi2mqtt.lib.app_settings import settings
from unifi2mqtt.lib.client import get_last_seen_for_client

logger = logging.getLogger(__name__)


def is_connected(client, timeout):
    now = time.time()
    last_seen = get_last_seen_for_client(client)
    logger.debug(
        f"Current time: {round(now)}, last seen: {last_seen} (difference: {round(now - last_seen)}s). Device is: " + (
            "online" if (now - last_seen) <= timeout else "offline"))
    return (now - last_seen) <= timeout


def login(session, url: str, login_payload: dict, ignore_ssl: bool):
    login_url = f"{url.rstrip('/')}/api/auth/login"
    if settings.verbose:
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


def fetch_clients(session, url: str, login_payload: dict, ignore_ssl: bool, site):
    return _request_with_reauth(session, url, login_payload, ignore_ssl, site, _get_clients)


def _get_clients(session, url: str, login_payload: dict, ignore_ssl: bool, site):
    clients_url = f"{url.rstrip('/')}/proxy/network/api/s/{site}/stat/sta"
    if settings.verbose:
        logger.debug(f"Fetching clients from {clients_url}")
    response = session.get(clients_url, verify=not ignore_ssl)
    response.raise_for_status()
    return response.json().get("data", [])


def _request_with_reauth(session, url: str, login_payload: dict, ignore_ssl: bool, site, action):
    try:
        return action(session, url, login_payload, ignore_ssl, site)
    except requests.HTTPError as e:
        if 400 <= e.response.status_code < 500:
            logger.warning(f"HTTP {e.response.status_code} - retrying after login.")
            login(session, url, login_payload, ignore_ssl)
            return action(session, url, login_payload, ignore_ssl, site)
        raise

def _site_exists(session, url, _login_payload, ignore_ssl, site):
    sites_url = f"{url.rstrip('/')}/proxy/network/api/self/sites"
    if settings.verbose:
        logger.debug("Checking site '%s' via %s", site, sites_url)

    resp = session.get(sites_url, verify=not ignore_ssl)
    resp.raise_for_status()

    data = resp.json().get("data", [])
    available = {entry.get("name") for entry in data if isinstance(entry, dict)}
    exists = site in available

    return exists

def site_exists(session, url: str, login_payload: dict, ignore_ssl: bool, site: str) -> bool:
    return _request_with_reauth(session, url, login_payload, ignore_ssl, site, _site_exists)
