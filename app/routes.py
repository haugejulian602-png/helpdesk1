from flask import Blueprint, render_template, request, redirect, url_for, abort
from datetime import datetime

from .storage import load_tickets, save_tickets, load_log, log_action

bp = Blueprint("main", __name__)

# Globale variabler (men vi refresher dem fra disk på hver request)
tickets = []
next_id = 1

# Navn brukt i arbeidsliste / auto-tildeling (hardkodet)
WORK_USER_NAME = "Julian"


def client_ip():
    return request.remote_addr or ""


def is_admin():
    ip = client_ip()
    return ip in ("127.0.0.1", "::1")


def require_admin():
    if not is_admin():
        abort(403, description="Du har ikke tilgang til denne handlingen.")


def normalize_ticket(t):
    t.setdefault("id", 0)
    t.setdefault("title", "")
    t.setdefault("description", "")
    t.setdefault("priority", "Lav")
    t.setdefault("status", "Åpen")
    t.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    t.setdefault("assignee", "")
    t.setdefault("comments", [])
    if not isinstance(t.get("comments"), list):
        t["comments"] = []
    return t


def refresh_state(save_if_changed: bool = True):
    """
    Laster tickets fra disk og normaliserer.
    Oppdaterer globale tickets + next_id.
    """
    global tickets, next_id

    loaded = load_tickets()
    changed = False

    normalized = []
    for t in loaded:
        before = dict(t) if isinstance(t, dict) else {}
        t = t if isinstance(t, dict) else {}
        t = normalize_ticket(t)
        normalized.append(t)
        if t != before:
            changed = True

    tickets = normalized
    next_id = (max([t.get("id", 0) for t in tickets], default=0) + 1)

    if save_if_changed and changed:
        save_tickets(tickets)


def find_ticket(ticket_id):
    for t in tickets:
        if t.get("id") == ticket_id:
            return t
    return None


def is_closed(t):
    return (t.get("status") or "").strip() == "Lukket"


def short_text(s: str, n: int = 60) -> str:
    s = (s or "").strip().replace("\n", " ")
    return (s[: n - 1] + "…") if len(s) > n else s


# Init-load ved oppstart
refresh_state(save_if_changed=True)


@bp.route("/", methods=["GET"])
def index():
    refresh_state(save_if_changed=True)

    q = (request.args.get("q") or "").strip().lower()

    normalized = [normalize_ticket(t) for t in tickets]
    sorted_tickets = sorted(normalized, key=lambda x: x.get("id", 0), reverse=True)

    if q:

        def comments_text(t):
            parts = []
            for c in (t.get("comments") or []):
                if isinstance(c, dict):
                    parts.append(str(c.get("name", "")))
                    parts.append(str(c.get("text", "")))
            return " ".join(parts).lower()

        def match(t):
            return (
                q in (t.get("title", "").lower())
                or q in (t.get("description", "").lower())
                or q in (t.get("status", "").lower())
                or q in (t.get("assignee", "").lower())
                or q in (t.get("priority", "").lower())
                or q in comments_text(t)
            )

        sorted_tickets = [t for t in sorted_tickets if match(t)]

    return render_template("index.html", tickets=sorted_tickets, is_admin=is_admin(), q=q)


@bp.route("/my_work", methods=["GET"])
def my_work():
    """
    Kun admin (localhost) kan se arbeidslista.
    Viser aktive saker (Åpen / Pågår) som enten er:
    - tildelt Julian, eller
    - ikke tildelt noen (tom assignee)
    """
    refresh_state(save_if_changed=True)
    require_admin()

    normalized = [normalize_ticket(t) for t in tickets]

    active = [t for t in normalized if t.get("status") in ("Åpen", "Pågår")]

    target = WORK_USER_NAME.strip().lower()
    filtered = []
    for t in active:
        assignee = (t.get("assignee") or "").strip().lower()
        if assignee == "" or assignee == target:
            filtered.append(t)

    filtered = sorted(filtered, key=lambda x: x.get("id", 0), reverse=True)
    return render_template("my_work.html", tickets=filtered, is_admin=is_admin())


@bp.route("/new", methods=["GET"])
def new_ticket():
    refresh_state(save_if_changed=True)
    return render_template("new_ticket.html", is_admin=is_admin())


@bp.route("/create", methods=["POST"])
def create_ticket():
    refresh_state(save_if_changed=True)

    global next_id, tickets

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    priority = (request.form.get("priority") or "Lav").strip()

    if not title:
        abort(400, description="Tittel kan ikke være tom.")

    t = {
        "id": next_id,
        "title": title,
        "description": description,
        "priority": priority if priority else "Lav",
        "status": "Åpen",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "assignee": "",
        "comments": [],
    }

    tickets.append(normalize_ticket(t))
    next_id += 1
    save_tickets(tickets)

    log_action(
        f"Opprettet sak: “{title}” (Prioritet: {t['priority']})",
        ticket_id=t["id"],
        by="user",
        ip=client_ip(),
        details={"title": title, "priority": t["priority"]},
    )
    return redirect(url_for("main.index"))


@bp.route("/ticket/<int:ticket_id>", methods=["GET"])
def ticket(ticket_id):
    refresh_state(save_if_changed=True)

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    t = normalize_ticket(t)
    return render_template("ticket.html", ticket=t, is_admin=is_admin())


@bp.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def set_status(ticket_id):
    refresh_state(save_if_changed=True)
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    if is_closed(t):
        abort(400, description="Denne saken er Lukket og kan ikke endres (status låst).")

    status = (request.form.get("status") or "").strip()
    if status not in ("Åpen", "Pågår", "Lukket"):
        abort(400, description="Ugyldig status.")

    old_status = t.get("status", "")
    t["status"] = status

    # Auto-tildel til Julian når status settes til "Pågår" og assignee er tom
    if status == "Pågår":
        current_assignee = (t.get("assignee") or "").strip()
        if current_assignee == "":
            t["assignee"] = WORK_USER_NAME
            log_action(
                f"Auto-tildelt ansvarlig ved Pågår: (tom) -> {WORK_USER_NAME}",
                ticket_id=ticket_id,
                by="admin",
                ip=client_ip(),
                details={"old_assignee": "", "new_assignee": WORK_USER_NAME},
            )

    normalize_ticket(t)
    save_tickets(tickets)

    log_action(
        f"Endret status: {old_status} -> {status}",
        ticket_id=ticket_id,
        by="admin",
        ip=client_ip(),
        details={"old_status": old_status, "new_status": status},
    )
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign(ticket_id):
    refresh_state(save_if_changed=True)
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    if is_closed(t):
        abort(400, description="Denne saken er Lukket og kan ikke endres (ansvarlig låst).")

    assignee = (request.form.get("assignee") or "").strip()
    old = (t.get("assignee") or "").strip()

    t["assignee"] = assignee
    normalize_ticket(t)
    save_tickets(tickets)

    old_disp = old if old else "(tom)"
    new_disp = assignee if assignee else "(tom)"

    log_action(
        f"Endret ansvarlig: {old_disp} -> {new_disp}",
        ticket_id=ticket_id,
        by="admin",
        ip=client_ip(),
        details={"old_assignee": old, "new_assignee": assignee},
    )
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/comment", methods=["POST"])
def add_comment(ticket_id):
    refresh_state(save_if_changed=True)
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    normalize_ticket(t)

    name = (request.form.get("name") or "admin").strip()
    text = (request.form.get("comment") or "").strip()
    if not text:
        return redirect(url_for("main.ticket", ticket_id=ticket_id))

    t["comments"].append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name": name,
            "text": text,
        }
    )
    save_tickets(tickets)

    log_action(
        f"Kommentar lagt til av {name}: “{short_text(text)}”",
        ticket_id=ticket_id,
        by="admin",
        ip=client_ip(),
        details={"name": name, "text_preview": short_text(text), "text_len": len(text)},
    )
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    refresh_state(save_if_changed=True)
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    title = t.get("title", "")

    tickets.remove(t)
    save_tickets(tickets)

    log_action(
        f"Slettet sak: “{title}”",
        ticket_id=ticket_id,
        by="admin",
        ip=client_ip(),
        details={"title": title},
    )
    return redirect(url_for("main.index"))


@bp.route("/activity", methods=["GET"])
def activity():
    require_admin()
    log = load_log()
    log = list(reversed(log))
    return render_template("activity.html", log=log, is_admin=True)


@bp.app_errorhandler(400)
def bad_request(e):
    message = getattr(e, "description", "Ugyldig forespørsel.")
    return render_template("error.html", code=400, message=message, is_admin=is_admin()), 400


@bp.app_errorhandler(403)
def forbidden(e):
    message = getattr(e, "description", "Du har ikke tilgang til denne handlingen.")
    return render_template("error.html", code=403, message=message, is_admin=is_admin()), 403
