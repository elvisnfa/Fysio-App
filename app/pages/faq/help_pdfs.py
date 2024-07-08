from dash import Dash, html

def load_layout_pdfs():
    return html.Div([
        html.H1("PDF's - Uitleg", className='text-center mb-4'),
        html.P(
            "Op deze pagina kun je de PDF-bestanden beheren die in de database aanwezig zijn. "
            "Hier is een uitleg van de verschillende onderdelen en functies van deze pagina:"
        ),

        html.H2("Bestand Toevoegen", className='mt-4'),
        html.P(
            "In deze sectie kun je nieuwe PDF-bestanden toevoegen aan de database. "
            "Je kunt bestanden slepen of klikken om een bestand te selecteren. "
            "De geselecteerde bestanden worden in de wachtrij geplaatst voor verwerking."
        ),
        html.Img(src='/assets/images/pdfs/bestand-toevoegen.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("PDF's in wachtrij", className='mt-4'),
        html.P(
            "Deze sectie toont een tabel met PDF-bestanden die in de wachtrij staan om verwerkt te worden. "
            "Je kunt de wachtrij beheren door bestanden te verwijderen of de naam van de bestanden aan te passen. "
            "Als je klaar bent om bestanden naar de database te sturen, klik je op de verwerk pdf knop. "
            "Er zal dan een laad icoontje verschijnen voor de start van het toevoegen van de pdf's aan de database."
        ),
        html.Img(src='/assets/images/pdfs/pdfs-in-wachtrij.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("PDF's aanwezig in de database", className='mt-4'),
        html.P(
            "Deze sectie toont een tabel met alle PDF's die momenteel in de database aanwezig zijn. "
            "Je kunt de naam van de PDF's bewerken of de PDF's verwijderen uit de database."
        ),
        html.Img(src='/assets/images/pdfs/pdfs-in-database.gif',
                 className='img-fluid', style={'margin': '20px 0'}),


        html.H2("Extra Functionaliteiten", className='mt-4'),
        html.P(
            "In deze sectie vind je extra functies zoals "
            "het trainen van een nieuw topic model op paragraph of page level. "
            "Het retrainen zorgt voor een update van de machine learning topics (o.b.v. de huidige database). "
            "Ook is er een knop voor het starten van de Web Scraper. "
            "Dit haalt automatisch FysioPraxis pdf's van het internet op."
            "Deze extra functies helpen bij het verwerken en analyseren van de PDF-bestanden."
        ),
        html.Img(src='/assets/images/pdfs/extra.png',
                 className='img-fluid', style={'margin': '20px 0'}),
    ])

def register_pdfs_callbacks(app: Dash):
    pass