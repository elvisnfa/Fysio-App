

from dash import Dash, Input, Output, State
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.html import H1
from dash_bootstrap_components import Button, Col
from dash_bootstrap_components import Input as B_Input
from dash_bootstrap_components import Row
from sqlalchemy.orm import Session
from utils.database import DB_ENGINE, BadWord, get_table_as_df

from .main import WORDS_PAGE_PATH


def load_layout_bw_page():
    return [
        H1("Stopwoorden", className='text-center mb-4'),

        Row([
            Col(
                B_Input(
                    id='new-word-input',
                    type='text',
                    placeholder="Nieuw word"
                )
            ),
            Col(
                Button(
                    "Voeg woord toe",
                    id="add-word-btn",
                    className="word-button",
                )
            )
        ], className='my-4'),

        DataTable(
            id='wordlist-table',
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
                }
            ],
            data=(
                get_table_as_df(BadWord).to_dict("records")
            ),
            editable=True,
            row_deletable=True,
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


def register_bad_words_callbacks(app: Dash):
    @app.callback(
        Output('wordlist-table', 'data'),
        Input('wordlist-table', 'data_previous'),
        State('wordlist-table', 'data'),
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
                    word = session.query(BadWord).filter_by(id=prev_row['id']).first()

                    if not current_row:
                        session.delete(word)
                    else:
                        word.word = current_row['word']

                    session.commit()

        return data_current

    @app.callback(
        Output('url', 'href', allow_duplicate=True),
        [
            Input('add-word-btn', 'n_clicks'),
            Input('new-word-input', 'value')
        ],
        prevent_initial_call=True
    )
    def add_new_word(n_clicks, word):
        if not n_clicks or not word or not type:
            raise PreventUpdate

        with Session(DB_ENGINE) as session:
            session.add(
                BadWord(word=word)
            )
            session.commit()

        return WORDS_PAGE_PATH
