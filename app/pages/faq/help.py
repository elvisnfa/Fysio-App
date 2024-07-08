from dash import Dash, Input, Output, register_page
from dash.html import Div, P
from dash_bootstrap_components import Container, Tab, Tabs

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR

HELP_PAGE_PATH = '/help'

layout = Div([
    Container(
        Tabs(
            [
                Tab(
                    label="Grafieken",
                    tab_id="grafieken"
                ),
                Tab(
                    label="Pagina Resultaten",
                    tab_id="pagina-resultaten"
                ),
                Tab(
                    label="PDF's",
                    tab_id="pdfs"
                ),
                Tab(
                    label="Woorden",
                    tab_id="woorden"
                )
            ],
            id="nav-tabs-words",
            active_tab="grafieken",
        )
    ),
    Container(id="faq-page-container")
])

register_page(
    __name__,
    path=HELP_PAGE_PATH,
    layout=layout,
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Help"
)

def register_help_callbacks(app: Dash):
    from .help_grafieken import load_layout_grafieken, register_grafieken_callbacks
    register_grafieken_callbacks(app)
    from .help_pagina_resultaten import load_layout_pagina_resultaten, register_pagina_resultaten_callbacks
    register_pagina_resultaten_callbacks(app)
    from .help_pdfs import load_layout_pdfs, register_pdfs_callbacks
    register_pdfs_callbacks(app)
    from .help_woorden import load_layout_woorden, register_woorden_callbacks
    register_woorden_callbacks(app)

    @app.callback(
        Output("faq-page-container", "children"),
        Input("nav-tabs-words", "active_tab"),
    )
    def switch_tab(active_tab):
        if active_tab == "grafieken":
            return load_layout_grafieken()
        elif active_tab == "pagina-resultaten":
            return load_layout_pagina_resultaten()
        elif active_tab == "pdfs":
            return load_layout_pdfs()
        elif active_tab == "woorden":
            return load_layout_woorden()
        return [P("Something went wrong...")]