README Helpdesk Flask v1.0

Prosjektnavn
help_desk1

Hva er dette prosjektet
Dette prosjektet er en enkel helpdesk laget med Flask (Python). Brukere kan sende inn saker (tickets) med tittel, beskrivelse og prioritet. Sakene vises i en oversikt, og man kan åpne en sak for å se detaljer og lukke den når den er ferdig.

Hva kan helpdesken gjøre
- Lage ny sak
- Vise alle saker i en oversikt
- Åpne en sak og se detaljer
- Lukke en sak (status blir Lukket)
- Slette en sak (kun admin)
- Skrive ut alle saker i terminalen via en debug-side

Hvordan lagring fungerer
Sakene lagres i en fil som heter tickets.json i rotmappa. Det gjør at sakene ikke forsvinner når serveren restartes.

Admin
Jeg er admin når jeg bruker helpdesken på samme maskin som serveren kjører på (localhost). Andre som åpner helpdesken fra en annen PC på nettverket er vanlige brukere og kan ikke slette saker.

Filstruktur
- app.py starter programmet
- app/__init__.py lager Flask appen og kobler på routes
- app/routes.py inneholder alle sidene (routes) og logikk for saker
- app/storage.py lagrer og henter saker fra tickets.json
- app/templates inneholder html-filene
- app/static inneholder css

Hvordan starte prosjektet lokalt
1. Åpne terminal i prosjektmappa help_desk1
2. Aktiver virtuell miljø
source .venv/bin/activate
3. Installer Flask hvis det trengs
python -m pip install flask
4. Start appen
python app.py
5. Åpne i nettleser
http://127.0.0.1:5050

Hvordan teste med en annen PC på samme nettverk
Når serveren kjører på nettverket kan en annen PC på samme WiFi åpne helpdesken med IP-adressen til server-PCen og port 5050.
Eksempel:
http://DIN_IP:5050

IP kan finnes på Mac med:
ipconfig getifaddr en0

Debug
For å skrive ut alle saker i terminalen kan man åpne:
http://127.0.0.1:5050/debug/print

Videre arbeid (to do)
- Legge til kategori på saker (nettverk, programvare, utstyr)
- Filtrere mellom åpne og lukkede saker
- Søke i saker
- Forbedre design og layout
