from flask import Flask, render_template, request, redirect, url_for

# Oppretter Flask‑applikasjonen
app = Flask(__name__)

# Midlertidig lagring av «saker» som en liste av ordbøker
tickets = []

@app.route('/')
def index():
    """Hjemmeside: viser alle eksisterende saker."""
    return render_template('index.html', tickets=tickets)

@app.route('/create', methods=['GET', 'POST'])
def create_ticket():
    """
    Skjema for å lage ny sak.
    Når siden lastes med GET viser den et skjema.
    Ved POST henter den data fra skjemaet og legger til en ny sak.
    """
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Legg til ny sak med et enkelt løpenummer.
        ticket_id = len(tickets) + 1
        tickets.append({'id': ticket_id, 'title': title, 'description': description})
        # Når saken er lagret, send brukeren tilbake til forsiden
        return redirect(url_for('index'))
    return render_template('create_ticket.html')

@app.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):
    """Viser en enkel detaljside for én sak."""
    # Finn riktig sak basert på id
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    return render_template('ticket_detail.html', ticket=ticket)

# Starter serveren når filen kjøres direkte
if __name__ == '__main__':
    app.run(debug=True)
