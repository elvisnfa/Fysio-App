

from dash import Dash, Input, Output, State, no_update
from dash.dash_table import DataTable
from dash.dcc import Dropdown
from dash.html import H1
from dash_bootstrap_components import Button, Col
from dash_bootstrap_components import Input as B_Input
from dash_bootstrap_components import Row
from sqlalchemy.orm import Session
from utils.database import DB_ENGINE, WordObject, get_table_as_df, recalculate_complexity_for_all_magazines


from .main import WORDS_PAGE_PATH


def load_layout_rw_page():
    return [
        H1("Relevante woorden", className='text-center mb-4'),

        Row([
            Col(
                B_Input(
                    id='new-r-word-input',
                    type='text',
                    placeholder="Nieuw word"
                )),
            Col(Dropdown(
                id='new-r-word-type',
                options=[
                    {'label': 'Reductionistisch', 'value': '1'},
                    {'label': 'Complex', 'value': '2'},
                    {'label': 'Antoniem', 'value': '3'}
                ],
                placeholder="Selecteer type"
            )),
            Col(B_Input(
                id='new-r-word-weight',
                type='number',
                placeholder="Nieuw gewicht"
            )),
            Col(Button(
                "Voeg woord toe",
                id="add-r-word-btn",
                className="word-button",
            )),
            Col(Button(
                "Herbereken complexiteit scores",
                id="recalculate-complexity-scores-btn",
                className="word-button",
            )),
        ], className='my-4'),

        DataTable(
            id='relevant-wordlist-table',
            columns=[
                {
                    'name': 'ID',
                    'id': 'id',
                    'editable': False
                },
                {
                    'name': 'Woord',
                    'id': 'word',
                    'editable': True
                },
                {
                    'name': 'Type',
                    'id': 'type',
                    'presentation': 'dropdown',
                    'editable': True
                },
                {
                    'name': 'Gewicht',
                    'id': 'weight',
                    'editable': True,
                    'type': 'numeric'
                },
            ],
            data=get_table_as_df(WordObject).to_dict("records"),
            editable=True,
            row_deletable=True,
            dropdown={
                'type': {
                    'options': [
                        {'label': 'Reductionistisch', 'value': '1'},
                        {'label': 'Complex', 'value': '2'},
                        {'label': 'Antoniem', 'value': '3'}
                    ]
                }
            },
            filter_action='native',
            sort_action='native',
            page_action='native',
            css=[
                {"selector": ".Select-menu-outer",
                 "rule": "display: block !important"}
            ],
            style_data_conditional=[
                {
                    'if': {
                        'column_editable': False
                    },
                    'cursor': 'not-allowed'
                },
            ],
        )
    ]


def register_relevant_words_callbacks(app: Dash):
    @app.callback(
        Output('relevant-wordlist-table', 'data'),
        Input('relevant-wordlist-table', 'data_previous'),
        State('relevant-wordlist-table', 'data'),
        prevent_initial_call=True
    )
    def update_database(data_previous, data_current):
        prev_dict = {item['id']: item for item in data_previous}
        current_dict = {item['id']: item for item in data_current}

        all_ids = set(prev_dict.keys()).union(current_dict.keys())

        zipped_data = [(prev_dict.get(id), current_dict.get(id))
                       for id in all_ids]

        with Session(DB_ENGINE) as session:
            for prev_row, current_row in zipped_data:
                if prev_row != current_row:
                    word = session.query(WordObject).filter_by(
                        id=prev_row['id']).first()

                    if not current_row:
                        session.delete(word)
                    else:
                        word.word = current_row['word']
                        word.type = current_row['type']
                        word.weight = current_row['weight']

                    session.commit()

        return data_current

    @app.callback(
        Output('url', 'href', allow_duplicate=True),
        [
            Input('add-r-word-btn', 'n_clicks'),
            Input('new-r-word-input', 'value'),
            Input('new-r-word-type', 'value'),
            Input('new-r-word-weight', 'value'),
        ],
        prevent_initial_call=True
    )
    def add_new_word(n_clicks, word, type, weight):
        if not n_clicks or not word or not type:
            return no_update

        with Session(DB_ENGINE) as session:
            session.add(
                WordObject(
                    word=word,
                    type=type,
                    weight=weight
                )
            )
            session.commit()

        return WORDS_PAGE_PATH

    @app.callback(
        Output("recalculation-loading-output",
               "children", allow_duplicate=True),
        Input('recalculate-complexity-scores-btn', 'n_clicks'),
        running=[
            (Output("recalculate-complexity-scores-btn", "disabled"), True, False),
        ],
        prevent_initial_call=True
    )
    def recalculate_complexity_scores(n_clicks):
        if not n_clicks:
            return no_update

        recalculate_complexity_for_all_magazines()

        return no_update
