from dataclasses import dataclass
from datetime import datetime

@dataclass
class Ticket:
    id: int
    title: str
    description: str
    priority: str
    status: str
    created: str

class TicketStore:
    def __init__(self):
        self._tickets = []
        self._next_id = 1

    def all(self):
        return list(reversed(self._tickets))  # nyeste øverst

    def add(self, title, description, priority):
        t = Ticket(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            status="Åpen",
            created=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self._tickets.append(t)
        self._next_id += 1

    def get(self, ticket_id):
        return next((t for t in self._tickets if t.id == ticket_id), None)

    def close(self, ticket_id):
        t = self.get(ticket_id)
        if t:
            t.status = "Lukket"
