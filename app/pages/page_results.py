import ast
import json
import re
from collections import Counter

from dash import Dash, Input, Output, dcc, html, register_page
from dash_bootstrap_components import Badge, Col, Container, Row
from plotly import graph_objects as go
from utils import database as db

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR


def load_layout():
    load_page_df()
    load_magazine_df()
    load_word_list()

    dropdown_options = (
        [
            {'label': row['name'], 'value': row['id']}
            for _, row in magazine_df.iterrows()
        ]
        if not magazine_df.empty else []
    )

    return Container([
        Row([
            Col([
                html.H2('Selecteer een magazine:'),
                dcc.Dropdown(
                    id='magazine-dropdown',
                    options=dropdown_options,
                    multi=False,
                    optionHeight=80,
                    maxHeight=500
                ),
                html.H2('Selecteer een pagina:'),
                dcc.Dropdown(
                    id='page-dropdown',
                    multi=False,
                    maxHeight=300,
                    options=[]
                ),
                html.H2('Woorden legenda:'),
                html.H3('Reductionistisch', style={'color': 'var(--nord11)'}),
                html.H3('Complex', style={'color': 'var(--nord10)'}),
                html.H3('Antoniemen', style={'color': 'var(--nord13)'}),
                dcc.Store(id='color-values'),
                html.Div(id='topic-pie',
                         className='results-graph-card')
            ], className='side-bar'),
            html.Div([
                html.H2('Complexiteit per pagina'),
                html.Div(
                    id='complexity_graph',
                    className='results-graph-card'),
                html.H2('Pagina Tekst:'),
                html.Div(
                    className='results-card',
                    id='text', style={
                        'maxHeight': '1000px',
                        'overflowX': 'hidden',
                        'whiteSpace': 'pre-wrap',
                        'textOverflow': 'ellipsis'
                    })
            ], className='side-content')
        ], className='content')
    ])


register_page(
    __name__,
    path='/pagina_resultaten',
    layout=load_layout,
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Page results"
)


def load_magazine_df():
    global magazine_df
    magazine_df = db.get_table_as_df(db.Magazine)


def load_page_df():
    global page_df
    page_df = db.get_table_as_df(db.Page)
    if not page_df.empty:
        page_df['pagina_nummer'] = \
            page_df.groupby('magazine_id').cumcount() + 1
        page_df['page_text'] = page_df['page_text'].apply(eval)


def load_word_list():
    global word_list_df
    word_list_df = db.get_table_as_df(db.WordObject)


def mark_words_from_wordlist(text, topic_list, bar_data):
    marked_text = []
    text = [' '.join(sublist) for sublist in text]
    for idx, paragraph in enumerate(text):

        # tijdelijke fix voor index error(topic index moet matchen met tekst)
        topic = topic_list[idx]
        for topic_color in bar_data:
            if topic_color[0] == topic:
                color = topic_color[1]
                break

        tooltip_str = "topic: ", topic
        marked_text.append(
            Badge(
                tooltip_str,
                color=color
            )
        )
        marked_text.append(html.Br())
        for _, row in word_list_df.iterrows():
            word = row['word']
            word_type = row['type']
            pattern = fr'\b{re.escape(word)}\b'
            match = bool(re.search(pattern, paragraph))

            if match:
                if match:
                    if word_type == '1':
                        color = '#BF616A'
                    elif word_type == '2':
                        color = '#5E81AC'
                    elif word_type == '3':
                        color = '#EBCB8B'
                    else:
                        color = 'white'
                    text_parts = paragraph.split(word)
                    marked_text.extend([html.Span(text_parts[0]),
                                        html.Span(word,
                                                  style={'color': color},
                                                  )])
                    if len(text_parts) > 1:
                        paragraph = text_parts[1]

        marked_text.append(
            html.Span(paragraph, id="paragraph-tooltip-target"+str(idx))
        )

        marked_text.append(html.Br())
        marked_text.append(html.Br())
        marked_text.append(html.Br())
    return marked_text


def create_complexity_graph_url(selected_magazine_id):
    if not isinstance(selected_magazine_id, list):
        selected_magazine_id = [selected_magazine_id]

    filtered_pages = page_df[page_df['magazine_id'].isin(selected_magazine_id)]

    page_labels = []
    page_complexity_sums = []
    complex_only_sum = []
    reduc_only_sum = []

    for _, row in filtered_pages.iterrows():
        page_labels.append(row['pagina_nummer'])
        complexity_scores = json.loads(row['complexity_scores'])

        page_complexity_sum = 0
        complex_sum = 0
        reduc_sum = 0
        for scores in complexity_scores:
            if scores:
                score = scores[0]
                page_complexity_sum += score
                if score > 0:
                    complex_sum += score
                elif score < 0:
                    reduc_sum += score

        page_complexity_sums.append(page_complexity_sum)
        complex_only_sum.append(complex_sum)
        reduc_only_sum.append(reduc_sum)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=page_labels,
        y=page_complexity_sums,
        mode='lines+markers',
        name='Total Score',
        hoverinfo='text',
        hovertext=[
            f"Pagina: {label}<br>Total Score: {score}"
            for label, score in zip(page_labels, page_complexity_sums)
        ],
        line=dict(color='#5E81AC'),
        marker=dict(color='#5E81AC', size=5)
    ))

    fig.add_trace(go.Scatter(
        x=page_labels,
        y=complex_only_sum,
        mode='lines+markers',
        name='Complex Score',
        hoverinfo='text',
        hovertext=[
            f"Pagina: {label}<br>Complex Score: {score}"
            for label, score in zip(page_labels, complex_only_sum)
        ],
        line=dict(color='#A3BE8C'),
        marker=dict(color='#A3BE8C', size=5)
    ))

    fig.add_trace(go.Scatter(
        x=page_labels,
        y=reduc_only_sum,
        mode='lines+markers',
        name='Reduction Score',
        hoverinfo='text',
        hovertext=[
            f"Pagina: {label}<br>Reduction Score: {score}"
            for label, score in zip(page_labels, reduc_only_sum)
        ],
        line=dict(color='#BF616A'),
        marker=dict(color='#BF616A', size=5)
    ))

    fig.update_layout(
        template="plotly_dark",
        clickmode='event+select',
        title='Complexiteit lijn grafiek',
        xaxis_title='Pagina',
        yaxis_title='Complexiteitsscore',
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        height=400,
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#434C5E',
                     zeroline=True, zerolinecolor='#434C5E')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#434C5E',
                     zeroline=True, zerolinecolor='#434C5E')

    return dcc.Graph(id='complexity-graph', figure=fig)


def topic_pie_url(selected_magazine_ids, page):
    if not selected_magazine_ids or not page:
        return go.Figure()

    magazine = []
    magazine.append(selected_magazine_ids)
    filtered_pages = page_df[page_df['magazine_id'].isin(magazine)]
    filtered_pages = filtered_pages.iloc[page-1]['par_topics']
    filtered_pages = ast.literal_eval(filtered_pages)

    page_topic_sum = Counter(filtered_pages)

    labels = list(page_topic_sum.keys())
    values = list(page_topic_sum.values())

    sorted_data = sorted(zip(values, labels))
    sorted_values, sorted_labels = zip(*sorted_data)

    colors = [
        '#81A1C1', '#5E81AC', '#BF616A', '#D08770', '#EBCB8B',
        '#A3BE8C', '#B48EAD', '#88C0D0', '#D8DEE9', '#8FBCBB',
        '#738CA1', '#6A829A', '#A55661', '#B87359', '#D3BA7B',
        '#8FAE7B', '#9D719A', '#79AFBD', '#C5D1D9', '#81B3A2',
        '#667E8C', '#5C7382', '#AD5458', '#C06F4E', '#CBB371',
        '#799C6F', '#8C678C', '#6D9EA7', '#B4BEC9', '#76AFA0'
    ]

    fig = go.Figure(data=[go.Bar(
        y=sorted_labels,
        x=sorted_values,
        orientation='h',
        marker=dict(color=list(colors))
    )])
    fig.update_layout(
        template="plotly_dark",
        yaxis_visible=False,
        yaxis_showticklabels=False,
        title='ML topic analysis',
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        uniformtext_mode='hide',
    )
    fig.update_traces(textposition='inside', width=0.5)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#434C5E',
                     zeroline=True, zerolinecolor='#434C5E')

    bar_data = []
    for trace in fig.data:
        if isinstance(trace, go.Bar):
            labels = trace.y
            colors = trace.marker.color
            for label, color in zip(labels, colors):
                bar_data.append((label, color))

    return fig, bar_data


def register_page_result_callbacks(app: Dash):
    @app.callback(
        [Output('topic-pie', 'children'),
         Output('color-values', 'data')],
        [Input('magazine-dropdown', 'value'),
         Input('page-dropdown', 'value')]
    )
    def update_topic_pie(selected_magazine, selected_page):
        if selected_magazine is None or selected_page is None:
            return "Nog geen tijdschrift & pagina geselecteerd.", None

        figure, bar_data = topic_pie_url(selected_magazine, selected_page)
        return dcc.Graph(figure=figure), bar_data

    @app.callback(
        Output('page-dropdown', 'options'),
        [Input('magazine-dropdown', 'value')]
    )
    def update_page_dropdown(selected_magazines):
        if not selected_magazines:
            return []

        selected_magazines = (
            [selected_magazines] if not isinstance(selected_magazines, list)
            else selected_magazines
        )
        filtered_pages = page_df[
            page_df['magazine_id'].isin(selected_magazines)
        ]

        page_dropdown_options = [{'label': str(row['pagina_nummer']),
                                  'value': row['pagina_nummer']}
                                 for _, row in filtered_pages.iterrows()]

        return page_dropdown_options

    @app.callback(
        Output('complexity_graph', 'children'),
        Input('magazine-dropdown', 'value')
    )
    def update_complexity_graph(selected_magazines):
        if not selected_magazines:
            return "Nog geen tijdschrift geselecteerd."
        return create_complexity_graph_url(selected_magazines)

    @app.callback(
        Output('text', 'children'),
        [Input('magazine-dropdown', 'value'),
         Input('page-dropdown', 'value'),
         Input('color-values', 'data')]
    )
    def update_text(selected_magazine, selected_page, bar_data):
        if selected_magazine is None or selected_page is None:
            return "Nog geen pagina geselecteerd"
        selection_predicate = (page_df['magazine_id'] == selected_magazine) & (page_df['pagina_nummer'] == selected_page)

        selected_text = page_df[selection_predicate]['page_text'].values[0]
        selected_topics = page_df[selection_predicate]['par_topics'].values[0]

        selected_topics = ast.literal_eval(selected_topics)

        selected_text = mark_words_from_wordlist(
            selected_text,
            selected_topics,
            bar_data
        )
        return selected_text

    @app.callback(
        Output('page-dropdown', 'value', allow_duplicate=True),
        [Input('complexity-graph', 'clickData')],
        prevent_initial_call=True
    )
    def display_click_data(clickData):
        if clickData:
            return clickData['points'][0]['x']
