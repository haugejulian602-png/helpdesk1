from flask import Blueprint, render_template, request, redirect, url_for, session
from .storage import find_user
from .storage import (
    load_tickets,
    create_ticket,
    get_ticket,
    update_ticket_status,
    delete_ticket
)

bp = Blueprint("main", __name__)
def require_login():
    if not session.get("user"):
        return redirect(url_for("main.login"))
    return None

@bp.route("/")
def index():
    tickets = load_tickets()
    return render_template("index.html", tickets=tickets)

@bp.route("/new")
def new_ticket():
    return render_template("new_ticket.html")

@bp.route("/create", methods=["POST"])
def create_ticket_route():
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not title:
        return "Tittel kan ikke være tom", 400

    create_ticket(title, description)
    return redirect(url_for("main.index"))

@bp.route("/ticket/<int:ticket_id>")
def ticket(ticket_id):
    t = get_ticket(ticket_id)
    if not t:
        return "Ticket ikke funnet", 404
    return render_template("ticket.html", ticket=t)

@bp.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def change_status(ticket_id):
    status = request.form.get("status")

    if status not in ("Åpen", "Pågår", "Lukket"):
        return "Ugyldig status", 400

    update_ticket_status(ticket_id, status)
    return redirect(url_for("main.ticket", ticket_id=ticket_id))

@bp.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket_route(ticket_id):
    delete_ticket(ticket_id)
    return redirect(url_for("main.index"))
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        user = find_user(username, password)
        if user:
            session["user"] = user["username"]
            return redirect(url_for("main.index"))
        return render_template("login.html", error="feil brukernavn eller passord")

    return render_template("login.html")
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))