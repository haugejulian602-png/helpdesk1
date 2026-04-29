from .db import get_db

def load_tickets():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = cur.fetchall()
    conn.close()
    return tickets

def create_ticket(title, description):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tickets (title, description, status, created_at)
        VALUES (%s, %s, %s, DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i'))
        """,
        (title, description, "Åpen")
    )
    conn.commit()
    conn.close()

def get_ticket(ticket_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
    ticket = cur.fetchone()
    conn.close()
    return ticket

def update_ticket_status(ticket_id, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tickets SET status = %s WHERE id = %s",
        (status, ticket_id)
    )
    conn.commit()
    conn.close()

def delete_ticket(ticket_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
    conn.commit()
    conn.close()
    def find_user(username, password):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT username FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cur.fetchone()
    conn.close()
    return user 