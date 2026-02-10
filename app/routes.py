from flask import Blueprint, render_template, request, redirect, url_for, abort
from datetime import datetime

from .storage import load_tickets, save_tickets, load_log, log_action

bp = Blueprint("main", __name__)

tickets = load_tickets()
next_id = (max([t.get("id", 0) for t in tickets], default=0) + 1)


def is_admin():
    ip = request.remote_addr or ""
    return ip in ("127.0.0.1", "::1")


def require_admin():
    if not is_admin():
        abort(403)


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


def normalize_all():
    global tickets, next_id
    changed = False
    for i, t in enumerate(tickets):
        before = dict(t)
        tickets[i] = normalize_ticket(t)
        if tickets[i] != before:
            changed = True
    if changed:
        save_tickets(tickets)
    next_id = (max([t.get("id", 0) for t in tickets], default=0) + 1)


def find_ticket(ticket_id):
    for t in tickets:
        if t.get("id") == ticket_id:
            return t
    return None


normalize_all()


@bp.route("/", methods=["GET"])
def index():
    q = (request.args.get("q") or "").strip().lower()

    normalized = [normalize_ticket(t) for t in tickets]
    sorted_tickets = sorted(normalized, key=lambda x: x.get("id", 0), reverse=True)

    if q:
        def match(t):
            return (
                q in (t.get("title", "").lower())
                or q in (t.get("description", "").lower())
                or q in (t.get("status", "").lower())
                or q in (t.get("assignee", "").lower())
            )
        sorted_tickets = [t for t in sorted_tickets if match(t)]

    return render_template("index.html", tickets=sorted_tickets, is_admin=is_admin(), q=q)


@bp.route("/new", methods=["GET"])
def new_ticket():
    return render_template("new_ticket.html", is_admin=is_admin())


@bp.route("/create", methods=["POST"])
def create_ticket():
    global next_id, tickets

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    priority = (request.form.get("priority") or "Lav").strip()

    if not title:
        return "Tittel kan ikke være tom", 400

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
    tickets.append(t)
    next_id += 1
    save_tickets(tickets)

    log_action("Opprettet sak", ticket_id=t["id"], by="user")
    return redirect(url_for("main.index"))


@bp.route("/ticket/<int:ticket_id>", methods=["GET"])
def ticket(ticket_id):
    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404
    t = normalize_ticket(t)
    return render_template("ticket.html", ticket=t, is_admin=is_admin())


@bp.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def set_status(ticket_id):
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    status = (request.form.get("status") or "").strip()
    if status not in ("Åpen", "Pågår", "Lukket"):
        return "Ugyldig status", 400

    old = t.get("status", "")
    t["status"] = status
    normalize_ticket(t)
    save_tickets(tickets)

    log_action(f"Endret status: {old} -> {status}", ticket_id=ticket_id, by="admin")
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign(ticket_id):
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    assignee = (request.form.get("assignee") or "").strip()
    old = t.get("assignee", "")
    t["assignee"] = assignee
    normalize_ticket(t)
    save_tickets(tickets)

    log_action(f"Endret ansvarlig: {old} -> {assignee}", ticket_id=ticket_id, by="admin")
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/comment", methods=["POST"])
def add_comment(ticket_id):
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

    log_action("La til kommentar", ticket_id=ticket_id, by="admin")
    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    require_admin()

    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404

    tickets.remove(t)
    save_tickets(tickets)

    log_action("Slettet sak", ticket_id=ticket_id, by="admin")
    return redirect(url_for("main.index"))


@bp.route("/activity", methods=["GET"])
def activity():
    require_admin()
    log = load_log()
    log = list(reversed(log))
    return render_template("activity.html", log=log, is_admin=True)


@bp.app_errorhandler(403)
def forbidden(_e):
    return "403: Du har ikke tilgang til denne handlingen.", 403
