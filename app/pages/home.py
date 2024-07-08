from dash import register_page
from dash.html import H1, Div, P
from dash_bootstrap_components import Col, Container, Row

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR

register_page(
    __name__,
    path='/',
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Home"
)

layout = Container([
    Row(
        Col(
            Div([
                H1(
                    "Welkom bij de FysioPraxis en Ergotherapie analyse tool",
                    className="text-center"
                ),
                P(
                    "Deze tool is ontworpen om inzichten te verkrijgen uit geüploade pdf's van FysioPraxis en "
                    "Ergotherapie. Op de grafieken pagina zijn inzichtvolle grafieken te vinden die kunnen helpen bij "
                    "het bepalen van de complexiteit van een tijdschrift. Bij de PDF beheren pagina kunnen pdf's worden"
                    " toegevoegd voor analyse.",
                    className="lead text-center"
                )
            ]),
            width=8
        ),
        justify="center",
        align="center",
        className="h-50"
    ),
],
    fluid=True,
    className="py-5"
)
