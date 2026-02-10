import json
from pathlib import Path
from datetime import datetime

TICKETS_FILE = Path("tickets.json")
LOG_FILE = Path("activity_log.json")


def load_tickets():
    if not TICKETS_FILE.exists():
        return []
    try:
        with TICKETS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_tickets(tickets):
    with TICKETS_FILE.open("w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)


def load_log():
    if not LOG_FILE.exists():
        return []
    try:
        with LOG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def log_action(action, ticket_id=None, by="admin", ip=None, details=None):
    """
    Backwards compatible:
    - gamle kall: log_action("...", ticket_id=1, by="admin") fungerer fortsatt
    Nye felt:
    - ip: request.remote_addr
    - details: dict med ekstra info (valgfritt)
    """
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": action,
        "ticket_id": ticket_id,
        "by": by,
    }

    if ip:
        entry["ip"] = ip
    if isinstance(details, dict) and details:
        entry["details"] = details

    log = load_log()
    log.append(entry)

    with LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
