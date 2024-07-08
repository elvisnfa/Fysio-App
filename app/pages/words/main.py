
from dash import Dash, Input, Output, register_page
from dash.html import Div, P
from dash_bootstrap_components import Container, Tab, Tabs
from dash_bootstrap_components import Button, Container, Spinner

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR

WORDS_PAGE_PATH = '/woorden_beheren'


layout = Div([
    Container([
        Spinner(Div(
            id="recalculation-loading-output",
            style={
                'height': '50px',
            }
        )),
        Tabs(
            [
                Tab(
                    label="Relevante woorden",
                    tab_id="relevant-words"
                ),
                Tab(
                    label="Stopwoorden",
                    tab_id="bad-words"
                ),
            ],
            id="nav-tabs-words",
            active_tab="bad-words",
        )
    ]),
    Container(id="words-page-container")
])


register_page(
    __name__,
    path=WORDS_PAGE_PATH,
    layout=layout,
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Woorden beheer"
)


def register_words_callbacks(app: Dash):
    from .relevant_words import (load_layout_rw_page,
                                 register_relevant_words_callbacks)
    register_relevant_words_callbacks(app)
    from .bad_words import load_layout_bw_page, register_bad_words_callbacks
    register_bad_words_callbacks(app)

    @app.callback(
        Output("words-page-container", "children"),
        Input("nav-tabs-words", "active_tab"),
    )
    def switch_tab(active_tab):
        if active_tab == "relevant-words":
            return load_layout_rw_page()
        elif active_tab == "bad-words":
            return load_layout_bw_page()

        return [P("Something went wrong...")]
