# ToDo

## Backend

### Vercel Functionality
Gebruik de Vercel-test repository om tests uit te voeren
We gaan vanuit JS om de vijf seconden een refresh callen om de data te updaten.
- images command in [vercel.json](vercel.json) zodat afbeeldingen laden geoptimaliseerd kan worden, zie [hier](https://vercel.com/docs/project-configuration)

### Data_Analysis
- Hoe gaan we om memt transponder names? Momenteel gaat dit via excel files maar dit lijkt me niet efficient
- update-functies en variabelen niet rechtstreeks aanroepen, maar via getters.
- [data_analysis_branch.py](api/data_analysis_branch.py) incorporeren

### File structuring
bij bulds api.app toevoegen

### App.py

## Frontend

### Hoofdpagina
- logo's een beetje lager
- logo eddy merckx erbij
- logo ugent fixen
- klikken op logo = link naar site
- VELOZONE titel aanpassen, logo

### Start
Aanmaken van lege dataframes voor het opslaan van de data. Transponders koppelen aan namen (optioneel)

--> transponders worden gekoppeld aan namen, dataFrames moeten nog aangemaakt worden
- transponders moeten ook uit database verwijders kunnen worden
- start date = datum van vandaag

### Leaderboard
Streamen van het live-leaderboard op het scherm. --> testen op live data
- `back` knop toevoegen om terug te gaan naar de hoofdpagina (linksonder)
- op de onderkant van de pagina logo's van wielercentrum, cycling vlaanderen... toevoegen
- logo's naar rechts verschuiven
- met bootstrap rows en cols de titel en de gegevens incorporeren
- bad-man erop zetten?

### Stop Sessie
-Stoppen van alle dataverzameling en het sluiten van het leaderboard
--> zorgen dat je enkel kan stoppen wanneer er ook effectief een sessie is gestart
- keuze raportgeneratie moet niet gemaakt worden, dit is met een knop op de hoofdpagina
- knop die de hele site `reset` voor moest er ergens iets fout gaan
- automatisch stoppen met fetchen vanaf dat begintijd + compitieduratie + 5 minuten > huidige tijd

### Genereer rapporten
Maak rapporten op basis van de data die er verzameld is tijdens de sessie
--> downloadlink maken
- per transponder een apart rapport maken indien gevraagd.
- stijl moet overeenkomen met de rest van de website
- `back` knop toevoegen om terug te gaan naar de hoofdpagina

### Download report
- ook een `back` knop toevoegen om terug te gaan naar de hoofdpagina te gaan.

### Name configuration
- `back` knop toevoegen om terug te gaan naar de hoofdpagina

### Flag bits
Om de bits te kunnen gebruiken in Vercel moet je verbinden met redis. 