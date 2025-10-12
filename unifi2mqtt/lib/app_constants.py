from typing import Final

LAST_SEEN_FIELDS: Final[tuple[str, ...]] = ("last_seen", "_last_seen_by_uap", "_last_seen_by_usw", "_last_seen_by_ugw",
                                            "_last_reachable_by_gw")

PERSIST_FILE: Final[str] = "connected_clients.json"
