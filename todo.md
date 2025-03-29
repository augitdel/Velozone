# ToDo

## Hoofdpagina
![alt text](image-1.png)
bestaat uit verschillende knoppen die elk hun eigen acties oproppen als ze ingedrukt zijn v
- knop die de hele site `reset` voor moest er ergens iets fout gaan

DONE
### Start
Aanmaken van lege dataframes voor het opslaan van de data. Transponders koppelen aan namen (optioneel)

--> transponders worden gekoppeld aan namen, dataFrames moeten nog aangemaakt worden
--> transponders moeten ook uit database verwijders kunnen worden
### Leaderboard
Streamen van het live-leaderboard op het scherm. --> testen op live data
- `back` knop toevoegen om terug te gaan naar de hoofdpagina (en stop session knop rechtstreeks vanuit leaderbord)
- op de onderkant van de pagina logo's van wielercentrum, cycling vlaanderen... toevoegen
### Stop Sessie
-Stoppen van alle dataverzameling en het sluiten van het leaderboard
--> zorgen dat je enkel kan stoppen wanneer er ook effectief een sessie is gestart
- er moet effectief aangeduid worden of je al dan niet een PDF wilt genereren, anders moet er een pop-up komen die je prompt om een keuze te maken
### Genereer rapporten
Maak rapporten op basis van de data die er verzameld is tijdens de sessie
--> downloadlink maken
- per transponder een apart rapport maken en in een zipfile alles samenvoegen of laten kiezen of je het algemen rapport of je persoonlijk rapport wilt zien.

### Download report
- ook een `back` knop toevoegen om terug te gaan naar de hoofdpagina te gaan.

### Reset knop

### Vercel Functionality
Gebruik de Vercel-test repository om tests uit te voeren
We gaan vanuit JS om de vijf seconden een refresh callen om de data te updaten.
- images command in [vercel.json](vercel.json) zodat afbeeldingen laden geoptimaliseerd kan worden, zie [hier](https://vercel.com/docs/project-configuration)

### Data_Analysis
- Hoe gaan we om memt transponder names? Momenteel gaat dit via excel files maar dit lijkt me niet efficient
- update-functies en variabelen niet rechtstreeks aanroepen, maar via getters.
- [data_analysis_branch.py](api/data_analysis_branch.py) incorporeren