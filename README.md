# FysioPraxis Tijdschriften Analysetool

Welkom bij de FysioPraxis Tijdschriften Analysetool! Dit project is ontwikkeld als onderdeel van ons schoolproject en 
maakt gebruik van de Dash bibliotheek om tijdschriften van FysioPraxis te analyseren.

## Inhoudsopgave
1. [Overzicht](#overzicht)
2. [Functies](#functies)
3. [Installatie en opstarten app](#installatie-en-opstarten-app)
4. [Gebruik](#gebruik)
5. [Structuur van de Code](#structuur-van-de-code)

## Overzicht
De FysioPraxis Tijdschriften Analysetool biedt gebruikers de mogelijkheid om inzicht te krijgen in verschillende 
aspecten van de tijdschriften van FysioPraxis. Met behulp van een interactieve interface kunnen gebruikers data 
visualiseren en analyseren.

## Functies
- **Data Visualisatie:** Interactieve grafieken en diagrammen om gegevens te analyseren.
- **Tekstanalyse:** Mogelijkheid om tekst te analyseren en patronen te herkennen.
- **Gebruiksvriendelijke Interface:** Intuïtieve en eenvoudige navigatie via Dash.
- **Filteropties:** Diverse filters om data te sorteren en te bekijken op basis van specifieke criteria.

## Installatie en opstarten app
Volg de onderstaande stappen om de applicatie lokaal op je machine te installeren en te draaien:

1. **Clone de repository naar jouw locale machine**
2. **Navigeer naar de project folder:**
    ```bash
   cd *naam van project folder*
3. **installeer de vereiste dependencies:**
    ```bash
   pip install -r requirements.txt
4. **Navigeer naar de app folder:**
    ```bash
   cd app
5. **Start de app:**
    ```bash
   python app.py

## Gebruik
Start de applicatie op en je zult een window zien verschijnen, je kunt ook je webbrowser openen op 'http://127.0.0.1:8050'.
Nu je de interface voor je hebt, kan je van start gaan met het verkennen van alle functies. Om te beginnen is het handig
om een FysioPraxis tijdschrift te uploaden op de pdf pagina. Gebruik vervolgens de grafiek en pagina resultaten pagina's
om het tijdschrift te analyseren. 

Als je de applicatie met volledige database en model bestand voor topics wilt overzetten naar een andere machine, 
adviseren we je om een zip bestand te maken en die over te zetten naar de nieuwe machine.

## Structuur van de code
- **app.py:** De hoofdapplicatie file die de Dash server draait.
- **/assets:** Bevat css en twee json bestanden met een lijst van woorden die worden gebruikt bij de analyse. 
- **/pages:** Bevat de pagina's in de applicatie met de bijbehorende  visualisaties.
- **/utils:** Bevat alle python-files met logica voor de applicatie, bijvoorbeeld database code, webscraper voor 
tijdschriften en complexiteit berekening. 
- **/utils/topic:** Bevat alle logica voor het genereren van topics bij tekst. 