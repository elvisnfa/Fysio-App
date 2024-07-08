from dash import Dash, html

def load_layout_grafieken():
    return html.Div([
        html.H1("Grafieken - Uitleg", className='text-center mb-4'),
        html.P(
            "Op deze pagina kun je verschillende grafieken en visualisaties "
            "zien die gegenereerd worden op basis van geselecteerde tijdschriften. "
            "Hier is een uitleg van de verschillende onderdelen en functies van deze pagina:"
        ),


        html.H2("Magazine selecteren", className='mt-4'),
        html.P(
            "Bovenaan de pagina vind je een dropdown-menu waar je een of meerdere "
            "tijdschriften kunt selecteren. De geselecteerde tijdschriften worden "
            "gebruikt om de visualisaties te genereren."
        ),
        html.Img(src='/assets/images/grafieken/selecteer-tijdschrift.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Wordcloud", className='mt-4'),
        html.P(
            "De Wordcloud visualisatie toont de meest voorkomende woorden in de "
            "geselecteerde tijdschriften. Grotere woorden komen vaker voor."
        ),
        html.Img(src='/assets/images/grafieken/wordcloud.png',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Complexiteit lijn grafiek over tijd", className='mt-4'),
        html.P(
            "Deze grafiek toont de complexiteit van artikelen over tijd voor "
            "de geselecteerde tijdschriften. Het geeft inzicht in hoe de complexiteit "
            "van artikelen zich in de loop van de tijd heeft ontwikkeld. "
            "Je kan als gebruiker hoveren over een bolletje om informatie te krijgen over de magazine"
        ),
        html.Img(src='/assets/images/grafieken/complexiteit-over-tijd.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Machine Learning Topic Wordcloud", className='mt-4'),
        html.P(
            "Deze Wordcloud toont de topics die door een machine learning model "
            "zijn geïdentificeerd in de artikelen van de geselecteerde tijdschriften."
        ),
        html.Img(src='/assets/images/grafieken/ml-wordcloud.png',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Machine Learning Topic Pie Chart", className='mt-4'),
        html.P(
            "Deze taartdiagram visualiseert de verdeling van verschillende topics "
            "in de geselecteerde tijdschriften. Het geeft een overzicht van welke topics "
            "het meest voorkomen. Je kan als gebruiker hoveren over elk pie deel om meer informatie te krijgen. "
            "Ook kan je een topics (uit)filteren"
        ),
        html.Img(src='/assets/images/grafieken/ml-pie-chart.gif',
                 className='img-fluid', style={'margin': '20px 0'}),

        html.H2("Gemiddelde Complexity & Page Topic opsomming", className='mt-4'),
        html.P(
            "Deze scatter plot toont de gemiddelde complexiteit van pagina's "
            "en het aantal pagina's per topic in de geselecteerde tijdschriften. "
            "Het geeft inzicht in hoe complex verschillende topics zijn."
            "Je kan als gebruiker hoveren over een bolletje om informatie te krijgen."
        ),
        html.Img(src='/assets/images/grafieken/complexiteit-topic-opsomming.gif',
                 className='img-fluid', style={'margin': '20px 0'}),
    ])

def register_grafieken_callbacks(app: Dash):
    pass