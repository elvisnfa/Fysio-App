from dash import Dash, html

def load_layout_woorden():
    return html.Div([
        html.H1("Woorden - Uitleg", className='text-center mb-4'),
        html.P(
            "Op deze pagina kun je de woordenlijsten beheren. Hier is een uitleg van de verschillende "
            "onderdelen en functies van deze pagina:"
        ),


        html.H2("Relevante woorden", className='mt-4'),
        html.P(
            "Deze sectie toont een tabel met relevante woorden. "
            "De relevante woorden worden gebruikt voor het calculeren van de complexiteitsscores"
            "Je kunt nieuwe woorden toevoegen, bestaande woorden bewerken of verwijderen. "
            "Voor elk woord kun je ook het type en gewicht instellen. "
        ),
        html.Img(src='/assets/images/woorden/relevante-woorden.png',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Stopwoorden", className='mt-4'),
        html.P(
            "Deze sectie toont een tabel met stopwoorden. "
            "Met dit tabel kunnen woorden handmatig uit de wordclouds gehaald worden "
            "(die bijvoorbeeld niet belangrijk/relevant zijn)."
            "Je kunt nieuwe stopwoorden toevoegen, bestaande stopwoorden bewerken of verwijderen."
        ),
        html.Img(src='/assets/images/woorden/stopwoorden.png',
                 className='img-fluid', style={'margin': '20px 0'}),
    ])

def register_woorden_callbacks(app: Dash):
    pass