from dash import Dash, html

def load_layout_pagina_resultaten():
    return html.Div([
        html.H1("Pagina Resultaten - Uitleg", className='text-center mb-4'),
        html.P(
            "Op deze pagina kun je resultaten en complexiteitsgegevens van geselecteerde tijdschriftpagina's "
            "zien. Hier is een uitleg van de verschillende onderdelen en functies van deze pagina:"
        ),


        html.H2("Magazine selecteren", className='mt-4'),
        html.P(
            "Bovenaan de pagina vind je een dropdown-menu waar je een tijdschrift kunt selecteren. "
            "Na selectie van een tijdschrift kun je vervolgens een specifieke pagina selecteren "
            "door in de dropdown te kijken of een"
        ),
        html.Img(src='/assets/images/pagina_resultaten/selecteer-magazine.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Complexiteit per pagina", className='mt-4'),
        html.P(
            "Deze sectie toont een grafiek met de complexiteitsscore van elke pagina in het geselecteerde tijdschrift. "
            "Je kunt op de punten in de grafiek klikken om de complexiteitsscores van verschillende pagina's te zien."
        ),
        html.Img(src='/assets/images/pagina_resultaten/complexiteit-lijn.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Woorden legenda", className='mt-4'),
        html.P(
            "Deze sectie toont de legenda voor verschillende woorden die zijn gemarkeerd op basis van hun type, zoals "
            "reductionistisch, complex, of antoniemen."
        ),
        html.Img(src='/assets/images/pagina_resultaten/woorden-legenda.png',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Pagina Tekst", className='mt-4'),
        html.P(
            "Hier zie je de tekst van de geselecteerde pagina, met gemarkeerde woorden op basis van de woordenlijst. "
            "De woorden worden gemarkeerd met verschillende kleuren afhankelijk van hun type."
        ),
        html.Img(src='/assets/images/pagina_resultaten/pagina-tekst.png',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Machine Learning Topic Bar Chart", className='mt-4'),
        html.P(
            "Deze staafdiagram toont de verdeling van verschillende topics op de geselecteerde pagina. "
            "Het geeft een overzicht van welke topics het meest voorkomen."
        ),
        html.Img(src='/assets/images/pagina_resultaten/topic-analyses.gif',
                 className='img-fluid', style={'margin': '20px 0'}),
    ])

def register_pagina_resultaten_callbacks(app: Dash):
    pass