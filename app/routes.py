from flask import Blueprint, render_template, request, redirect, url_for, abort
from datetime import datetime
from .storage import load_tickets, save_tickets

bp = Blueprint("main", __name__)

tickets = load_tickets()
next_id = (max([t["id"] for t in tickets]) + 1) if tickets else 1


def is_admin():
    return request.remote_addr in ("127.0.0.1", "::1")


def find_ticket(ticket_id: int):
    for t in tickets:
        if t["id"] == ticket_id:
            return t
    return None


def print_all_tickets():
    print("\n--- ALLE SAKER ---")
    if not tickets:
        print("Ingen saker.")
    else:
        for t in tickets:
            print(f"#{t['id']} | {t['status']} | {t['priority']} | {t['title']}")
    print("--- SLUTT ---\n")


@bp.route("/")
def index():
    return render_template("index.html", tickets=list(reversed(tickets)), is_admin=is_admin())


@bp.route("/new", methods=["GET", "POST"])
def new_ticket():
    global next_id

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Lav")

        if not title or not description:
            return render_template("new_ticket.html", error="Fyll inn tittel og beskrivelse!", is_admin=is_admin())

        ticket = {
            "id": next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "Åpen",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        tickets.append(ticket)
        next_id += 1

        save_tickets(tickets)
        print("NY SAK:", ticket)
        print_all_tickets()

        return redirect(url_for("main.index"))

    return render_template("new_ticket.html", error=None, is_admin=is_admin())


@bp.route("/ticket/<int:ticket_id>")
def ticket(ticket_id):
    t = find_ticket(ticket_id)
    if not t:
        return "Fant ikke saken (404)", 404
    return render_template("ticket.html", ticket=t, is_admin=is_admin())


@bp.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    t = find_ticket(ticket_id)
    if t:
        t["status"] = "Lukket"
        save_tickets(tickets)
        print(f"LUKKET SAK: #{ticket_id}")
        print_all_tickets()

    return redirect(url_for("main.ticket", ticket_id=ticket_id))


@bp.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    if not is_admin():
        abort(403)

    global tickets
    tickets = [t for t in tickets if t["id"] != ticket_id]
    save_tickets(tickets)

    print(f"SLETTET SAK: #{ticket_id}")
    print_all_tickets()

    return redirect(url_for("main.index"))


@bp.route("/debug/print")
def debug_print():
    print_all_tickets()
    return "Skrev alle saker i terminalen ✅"
