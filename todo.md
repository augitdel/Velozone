# ToDo

## Hoofdpagina
![alt text](image-1.png)
bestaat uit verschillende knoppen die elk hun eigen acties oproppen als ze ingedrukt zijn v

DONE
### Start
Aanmaken van lege dataframes voor het opslaan van de data. Transponders koppelen aan namen (optioneel)

--> transponders worden gekoppeld aan namen, dataFrames moeten nog aangemaakt worden
--> transponders moeten ook uit database verwijders kunnen worden
### Leaderboard
Streamen van het live-leaderboard op het scherm. 
--> testen op live data
### Stop Sessie
Stoppen van alle dataverzameling en het sluiten van het leaderboard
--> zorgen dat je enkel kan stoppen wanneer er ook effectief een sessie is gestart
### Genereer rapporten
Maak rapporten op basis van de data die er verzameld is tijdens de sessie
--> downloadlink maken

### Vercel Functionality
Gebruik de Vercel-test repository om tests uit te voeren
We gaan vanuit JS om de vijf seconden een refresh callen om de data te updaten.
- images command in [vercel.json](vercel.json) zodat afbeeldingen laden geoptimaliseerd kan worden, zie [hier](https://vercel.com/docs/project-configuration)

### Data_Analysis
- Hoe gaan we om memt transponder names? Momenteel gaat dit via excel files maar dit lijkt me niet efficient
- average lap time berekenen adhv huidge avg laptime en aantal doorkomsten $n$