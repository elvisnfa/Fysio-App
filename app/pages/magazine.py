import base64
import io
import time
from multiprocessing import Process, cpu_count

import pandas as pd
from dash import Dash, Input, Output, State, no_update, register_page
from dash.dash_table import DataTable
from dash.dcc import Upload
from dash.html import H1, A, Div
from dash_bootstrap_components import Button, Container, Spinner
from sqlalchemy.orm import Session
from utils import pdf_processing as pdf
from utils import scraper
from utils.database import DB_ENGINE, Magazine, add_magazine, get_table_as_df
from utils.logging import build_logger
from utils.topic import page_topic, paragraph_topic

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR

log = build_logger(__name__)


MAGAZINE_PAGE_PATH = '/pdf_beheren'

pdfs_to_process = []


def load_layout():
    load_magazine_df()

    return Container(
        [
            Spinner(Div(
                id="upload-loading-output",
                style={
                    'height': '50px',
                }
            )),

            Div(
                [
                    Div(
                        [
                            H1(
                                "PDF's aanwezig in de database:",
                                className='text-center mb-4'
                            ),
                            DataTable(
                                id='magazine-table',
                                columns=[
                                    {'name': 'ID', 'id': 'id', 'editable': False},
                                    {'name': 'Naam', 'id': 'name', 'editable': True},
                                    {
                                        'name': 'Uitgiftedatum',
                                        'id': 'creation_date',
                                        'editable': False
                                    },
                                ],
                                row_deletable=True,
                                filter_action='native',
                                sort_action='native',
                                sort_mode='multi',
                                page_action='native',
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'column_editable': False
                                        },
                                        'cursor': 'not-allowed'
                                    },
                                ],
                                data=magazine_df.to_dict('records'),
                                style_table={
                                    'overflowY': 'auto',
                                    'maxHeight': '200px'
                                },
                            ),
                        ],
                        style={
                            "padding": "2rem",
                            "align-items": "center",
                            "justify-content": "space-around"
                        },
                        className="magazine-grid-item upper-magazine-grid-item"
                    ),
                    Div(
                        [
                            H1(
                                "Voeg een nieuw bestand toe:",
                                className='text-center mb-4'
                            ),
                            Upload(
                                id='upload-data',
                                children=Div([
                                    'Sleep of ',
                                    A('klik om bestand te selecteren.')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '100px',
                                    'display': 'flex',
                                    'align-items': 'center',
                                    'justify-content': 'center',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'user-select': 'none'
                                },
                                accept="application/pdf",
                                multiple=True
                            ),
                        ],
                        className="magazine-grid-item lower-magazine-grid-item"
                    ),
                    Div(
                        [
                            H1(
                                "PDF's in wachtrij:",
                                className='text-center mb-4'
                            ),
                            Div(
                                Button(
                                    "Verwerk PDF's naar database",
                                    id="start-upload-process-btn",
                                    className="my-2 w-50 magazine-button",
                                    n_clicks=0
                                ),
                                className="button-container"
                            ),
                            DataTable(
                                id='magazine-to-process-table',
                                columns=[
                                    {'name': 'Naam', 'id': 'name'},
                                ],
                                row_deletable=True,
                                filter_action='native',
                                sort_action='native',
                                sort_mode='multi',
                                page_action='native',
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'column_editable': False
                                        },
                                        'cursor': 'not-allowed'
                                    },
                                ],
                                data=[{'name': dic['name']}
                                      for dic in pdfs_to_process],
                                style_table={
                                    'overflowY': 'auto',
                                    'maxHeight': '200px'
                                },
                            ),
                        ],
                        className="magazine-grid-item lower-magazine-grid-item"
                    ),
                    Div(
                        [
                            H1(
                                "Extra Functionaliteiten",
                                className='text-center mb-4'
                            ),
                            Div(
                                [
                                    Button(
                                        "Retrain paragraph level topic  model",
                                        id="retrain_paragraph_model_btn",
                                        className="my-2 mx-2 w-25 magazine-button",
                                        n_clicks=0
                                    ),
                                    Button(
                                        "Retrain page level topic model",
                                        id="retrain_page_model_btn",
                                        className="my-2 mx-2 w-25 magazine-button",
                                        n_clicks=0
                                    ),
                                    Button(
                                        "Start Web Scrape",
                                        id="start-scrape-btn",
                                        className="my-2 mx-2 w-25 magazine-button",
                                        n_clicks=0
                                    ),
                                ],
                                className="button-container d-flex justify-content-center"
                            ),
                        ],
                        className="magazine-grid-item lower-magazine-grid-item"
                    ),
                ],
                className="magazine-visualization-grid",
                style={"padding": "2rem"}
            ),
        ],
        id="magazine-page-container"
    )


register_page(
    __name__,
    path=MAGAZINE_PAGE_PATH,
    layout=load_layout,
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Magazines"
)


def load_magazine_df():
    global magazine_df
    magazine_df = get_table_as_df(Magazine)

    if magazine_df.empty:
        data = {
            'id': pd.Series(dtype='int'),
            'name': pd.Series(dtype='object'),
            'hash': pd.Series(dtype='object'),
            'creation_date': pd.Series(dtype='datetime64[ns]'),
            'meta_data': pd.Series(dtype='object')
        }

        magazine_df = pd.DataFrame(data)


def upload_pdf_wrapper(data):
    try:
        log.info(f"Uploading {data['name']}")
        upload_pdf(data['name'], data['content'])
        log.info(f"Uploaded {data['name']}")
    except Exception as e:
        log.error(f"Failed to upload {data['name']}: {e}")

    return data['name']


def upload_pdf(filename, content):
    stream = io.BytesIO(base64.b64decode(content))
    current_hash = pdf.generate_file_hash(stream)

    load_magazine_df()
    if any(magazine_df['hash'] == current_hash):
        return

    add_magazine(
        df=pdf.extraction(stream),
        hash=current_hash,
        metadata=pdf.extract_metadata_pdf(stream),
        filename=filename
    )
    stream.close()


def register_magazine_callbacks(app: Dash):
    @app.callback(
        [
            Output("upload-loading-output", "children", allow_duplicate=True),
            Output('url', 'href', allow_duplicate=True)
        ],
        Input('start-upload-process-btn', 'n_clicks'),
        running=[
            (Output("start-upload-process-btn", "disabled"), True, False),
        ],
        prevent_initial_call=True
    )
    def handle_pdf_processing(n):
        global pdfs_to_process

        if not pdfs_to_process or n is None or n == 0:
            return no_update, no_update

        while(pdfs_to_process):
            active_processes = []
            processed_pdf_names = []

            i = 0
            while i < len(pdfs_to_process) or active_processes:
                while len(active_processes) < cpu_count() and i < len(pdfs_to_process):
                    pdf_data = pdfs_to_process[i]
                    process = Process(target=upload_pdf_wrapper, args=(pdf_data,))
                    process.start()
                    active_processes.append((pdf_data, process, time.time()))
                    i += 1

                for pdf_data, process, start_time in active_processes[:]:
                    elapsed_time = time.time() - start_time
                    if not process.is_alive():
                        process.join()
                        processed_pdf_names.append(pdf_data['name'])
                        active_processes.remove((pdf_data, process, start_time))
                    elif elapsed_time > 90:
                        process.terminate()
                        process.join()
                        log.error(
                            f"Process for {pdf_data['name']} was "
                            f"terminated after exceeding 90 seconds."
                        )
                        processed_pdf_names.append(pdf_data['name'])
                        active_processes.remove((pdf_data, process, start_time))

                pdfs_to_process = [
                    pdf
                    for pdf in pdfs_to_process
                    if pdf['name'] not in processed_pdf_names
                ]

        page_topic.run()
        paragraph_topic.run()

        return no_update, MAGAZINE_PAGE_PATH

    @app.callback(
        [
            Output("upload-loading-output", "children", allow_duplicate=True),
            Output('url', 'href', allow_duplicate=True)
        ],
        Input('start-scrape-btn', 'n_clicks'),
        running=[
            (Output("start-scrape-btn", "disabled"), True, False),
        ],
        prevent_initial_call=True
    )
    def handle_pdf_scrape(n):
        if n is None or n == 0:
            return no_update, no_update

        pdfs_to_process.extend(scraper.scrape())

        return no_update, MAGAZINE_PAGE_PATH

    @app.callback(
        [
            Output("upload-loading-output", "children", allow_duplicate=True),
            Output('url', 'href', allow_duplicate=True)
        ],
        [
            Input('upload-data', 'contents'),
            Input('upload-data', 'filename')
        ],
        prevent_initial_call=True
    )
    def handle_pdf_uploads(contents, filenames):
        if contents is None or not contents:
            return no_update, no_update

        # Process each file in the list of uploaded files
        for content, filename in zip(contents, filenames):
            _, content = content.split(',')

            pdfs_to_process.append({
                "name": filename,
                "content": content
            })

        # Assuming MAGAZINE_PAGE_PATH is a general redirection after uploads
        return no_update, MAGAZINE_PAGE_PATH

    @app.callback(
        Output('magazine-to-process-table', 'data'),
        Input('magazine-to-process-table', 'data_previous'),
        State('magazine-to-process-table', 'data'),
        prevent_initial_call=True
    )
    def update_pdf_to_process(data_previous, data_current):
        global pdfs_to_process

        if len(data_current) < len(data_previous):
            new_names = {pdf['name'] for pdf in data_current}
            pdfs_to_process = [
                pdf
                for pdf in pdfs_to_process
                if pdf['name'] in new_names
            ]
        else:
            for i, new_pdf in enumerate(data_current):
                if pdfs_to_process[i]['name'] != new_pdf['name']:
                    pdfs_to_process[i]['name'] = new_pdf['name']

        return data_current

    @app.callback(
        Output('magazine-table', 'data'),
        Input('magazine-table', 'data_previous'),
        State('magazine-table', 'data'),
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
                    magazine = session.query(Magazine).filter_by(
                        id=prev_row['id']
                    ).first()

                    if not current_row:
                        session.delete(magazine)
                    else:
                        magazine.name = current_row['name']

            session.commit()

        return data_current

    @app.callback(
        Output("upload-loading-output", "children", allow_duplicate=True),
        Input('retrain_page_model_btn', 'n_clicks'),
        running=[
            (Output("retrain_page_model_btn", "disabled"), True, False),
        ],
        prevent_initial_call=True
    )
    def retrain_page_model(n):
        page_topic.run(True)

        return None

    @app.callback(
        Output("upload-loading-output", "children", allow_duplicate=True),
        Input('retrain_paragraph_model_btn', 'n_clicks'),
        running=[
            (Output("retrain_paragraph_model_btn", "disabled"), True, False),
        ],
        prevent_initial_call=True
    )
    def retrain_par_model(n):
        paragraph_topic.run(True)

        return None
