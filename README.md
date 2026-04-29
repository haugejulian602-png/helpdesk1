Dette prosjektet er en enkel helpdesk laget med python og flask. Brukere kan opprette saker med tittel og beskrivelse. Alle saker vises på forsiden og man kan åpne en sak for å se detaljer endre status eller slette den.
Prosjektet er delt opp i flere filer for å gjøre koden mer oversiktlig. app.py starter flask serveren. I mappen app ligger backend koden. routes.py inneholder sidene i programmet og bestemmer hva som skjer når brukeren åpner en side. storage.py brukes til å lagre og hente saker.
html sidene ligger i templates og brukes til å vise innholdet i nettleseren. base.html er en felles mal som de andre sidene bruker. designet på siden styres av style.css som ligger i static mappen.
alle saker lagres i filen tickets.json. når en ny sak opprettes eller endres oppdaterer programmet denne filen slik at sakene ikke forsvinner når serveren restartes.
applikasjonen startes ved å kjøre python app.py og nettsiden kan åpnes i nettleseren på http 127.0.0.1

## Lisens
Dette prosjektet bruker MIT License.