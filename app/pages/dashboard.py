import plotly.express as px
import json
import urllib

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, register_page
from dash.dcc import Dropdown, Graph, Slider
from dash.html import H2, Div, Img, Label, P
from dash_bootstrap_components import Container
from plotly import graph_objects as go
from wordcloud import WordCloud

from app import PAGE_TITLE_BASE, PAGE_TITLE_SEPERATOR
from utils import database as db

WORDCLOUD_KEY = "Wordcloud"
COMPLEXITY_GRAPH_KEY = "Complexity Graph"
TOPIC_CLOUD_KEY = "Topic Wordcloud"
TOPIC_PIE_KEY = "Topic Pie"
PLOTLY_MARKER_SIZE = 8


def load_layout():
    load_stopwords()
    load_page_df()
    load_magazine_df()
    generate_color_map()

    dropdown_options = (
        [
            {'label': row['name'], 'value': row['id']}
            for _, row in magazine_df.iterrows()
        ]
        if not magazine_df.empty else []
    )
    default_dropdown_value = magazine_df['id'].tolist(
    ) if not magazine_df.empty else []

    topic_dropdown_options = (
        [
            {'label': topic, 'value': topic}
            for topic in page_df['page_topic'].apply(eval).unique().tolist()
        ]
        if not page_df.empty else []
    )

    return Container([
        Div([

            Div([
                H2('Selecteer tijdschrift(en):'),
                Dropdown(
                    id='magazine-dropdown',
                    options=dropdown_options,
                    multi=True,
                    value=default_dropdown_value,
                    maxHeight=500
                )
            ], className='top-bar'),

            Div([
                Div([
                    Div(
                        create_magazine_wordcloud_div(),
                        id='wordcloud-container',
                        className='dashboard-grid-item'
                    ),
                    Div(
                        H2('Complexiteit lijn grafiek over tijd:'),
                        id='complexity-graph-container',
                        className='dashboard-grid-item'
                    ),
                    Div(
                        H2('ML onderwerp(en):'),
                        id='topic-pie-container',
                        className='dashboard-grid-item'
                    ),
                    Div([
                        H2('ML onderwerp(en) populariteit:'),
                        Dropdown(
                            id='topic-dropdown',
                            options=topic_dropdown_options,
                            multi=True,
                            maxHeight=250,
                            className='topic-pop-dropdown'
                        ),
                        Div(id='topic-popularity-scatter')
                    ], className='dashboard-grid-item'),
                    Div(
                        H2('Gemiddelde complexiteit & pagina ml-onderwerp opsomming:'),
                        id='scatter-plot-container',
                        className='dashboard-grid-item'
                    ),
                    Div(
                        create_topic_word_cloud_div(),
                        id='topic-cloud-container',
                        className='dashboard-grid-item'
                    ),
                ], className='visualization-grid')
            ], className='bottom-content')

        ], className='content column-content')
    ])


register_page(
    __name__,
    path='/grafieken',
    layout=load_layout,
    title=PAGE_TITLE_BASE + PAGE_TITLE_SEPERATOR + "Grafieken"
)


def load_stopwords():
    global stop_words
    stop_words = set(db.get_table_as_df(db.BadWord)['word'].to_list())


def load_magazine_df():
    global magazine_df
    magazine_df = db.get_table_as_df(db.Magazine)


def load_page_df():
    global page_df

    def remove_stopwords(text):
        return [
            word
            for paragraph in text
            for word in paragraph
            if word.strip() not in stop_words
        ]

    df = db.get_table_as_df(db.Page)

    if not df.empty:
        df['tokenized_text'] = (
            df['tokenized_text'].apply(eval).apply(remove_stopwords)
        )

    page_df = df


def generate_color_map():
    """
    Generates a unique and visually distinct color map for given topics using HSV color space converted to RGB.

    Returns:
        dict: A dictionary mapping each topic to a unique color in HEX format.
    """
    global topic_color_map

    # Assuming 'page_df' contains the topics
    topics = page_df['page_topic'].apply(eval).unique().tolist()

    px_colors = px.colors.qualitative
    color_cycle = px_colors.Plotly + px_colors.Light24 + px_colors.Dark24

    # Loop over the topics and assign each topic a color from the cycle
    # If there are more topics than colors in the cycle, colors will repeat
    topic_color_map = {}
    cycle_length = len(color_cycle)

    for i, topic in enumerate(topics):
        # Use modulo to cycle through colors
        color = color_cycle[i % cycle_length]
        topic_color_map[topic] = color


def create_magazine_word_cloud(
    selected_magazine_ids,
    min_font_size,
    max_words
):
    """Generate a word cloud from selected magazine IDs."""
    if not selected_magazine_ids:
        return P("Nog geen tijdschrift geselecteerd.")

    filtered_pages = page_df[
        page_df['magazine_id'].isin(selected_magazine_ids)
    ]

    filtered_text = ' '.join([
        word
        for sublist in filtered_pages['tokenized_text']
        for word in sublist
    ])

    wordcloud = WordCloud(
        width=640,
        height=560,
        background_color="#3B4252",
        font_path='arial',
        stopwords=stop_words,
        min_font_size=min_font_size,
        max_words=max_words
    ).generate(filtered_text)

    img = wordcloud.to_svg()

    return Img(
        src=f'data:image/svg+xml;utf8,{urllib.parse.quote(img)}',
        width="640px",
        height="560px"
    )


def create_topic_word_cloud(
    selected_magazine_ids,
    min_font_size,
    max_words
):
    """Generate a word cloud from selected magazine IDs."""
    if not selected_magazine_ids:
        return P("Nog geen tijdschrift geselecteerd.")

    filtered_pages = page_df[
        page_df['magazine_id'].isin(selected_magazine_ids)
    ]

    filtered_text = ' '.join([
        str(topic)
        for topic in filtered_pages['page_topic']
        if topic is not None and "unknown" not in topic
    ])

    wordcloud = WordCloud(
        width=640,
        height=560,
        background_color="#3B4252",
        font_path='arial',
        min_font_size=min_font_size,
        max_words=max_words
    ).generate(filtered_text)

    img = wordcloud.to_svg()

    return Img(
        src=f'data:image/svg+xml;utf8,{urllib.parse.quote(img)}',
        width="640px",
        height="560px"
    )


def create_magazine_wordcloud_div(
    min_font_size=12,
    max_words=150
):
    return [
        H2('Wordcloud tijdschrift inhoud:'),
        Div(
            [
                Div([
                    Label('Minimale letter grootte'),
                    Slider(
                        id='magazine_wordcloud_min_font_size',
                        min=5,
                        max=30,
                        step=1,
                        value=min_font_size,
                        marks={i: str(i) for i in range(5, 31, 5)}
                    )
                ], className="wordcloud-slider-container"),
                Div([
                    Label('Maximaal aantal woorden'),
                    Slider(
                        id='magazine_wordcloud_max_words',
                        min=50,
                        max=500,
                        step=50,
                        value=max_words,
                        marks={i: str(i) for i in range(50, 501, 50)}
                    )
                ], className="wordcloud-slider-container"),
            ], className="wordcloud-parameters-container"
        )
    ]


def create_topic_word_cloud_div(
    min_font_size=12,
    max_words=150
):
    return [
        H2('Wordcloud ML onderwerpen:'),
        Div(
            [
                Div([
                    Label('Minimale letter grootte'),
                    Slider(
                        id='topic_wordcloud_min_font_size',
                        min=5,
                        max=30,
                        step=1,
                        value=min_font_size,
                        marks={i: str(i) for i in range(5, 31, 5)}
                    )
                ], className="wordcloud-slider-container"),
                Div([
                    Label('Maximaal aantal woorden'),
                    Slider(
                        id='topic_wordcloud_max_words',
                        min=50,
                        max=500,
                        step=50,
                        value=max_words,
                        marks={i: str(i) for i in range(50, 501, 50)}
                    )
                ], className="wordcloud-slider-container"),
            ], className="wordcloud-parameters-container"
        )
    ]


def topic_pie_url(selected_magazine_ids):
    if not selected_magazine_ids:
        return P("Nog geen tijdschrift geselecteerd.")

    filtered_pages = page_df[
        page_df['magazine_id'].isin(selected_magazine_ids)
    ]
    page_topic_sum = filtered_pages['page_topic']\
        .apply(eval)\
        .value_counts()\
        .reset_index()

    fig = go.Figure(data=[go.Pie(
        labels=page_topic_sum['page_topic'],
        values=page_topic_sum['count'],
        textposition='inside',
        insidetextorientation='radial',
        marker_colors=[
            topic_color_map.get(topic, '#333333')
            for topic in page_topic_sum['page_topic']
        ]
    )])
    fig.update_layout(
        template="plotly_dark",
        clickmode='event+select',
        showlegend=True,
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        height=650,
        width=1295,
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )
    fig.update_traces(textposition='inside')

    return Graph(id='pie-graph', figure=fig)


def create_complexity_graph(selected_magazine_ids):
    if not selected_magazine_ids:
        return P("Nog geen tijdschrift geselecteerd.")

    # Filter pages based on magazine IDs
    filtered_pages = page_df[page_df['magazine_id'].isin(
        selected_magazine_ids)]

    # Calculate the complexity sums for each magazine
    magazine_complexity_sums = {}
    for _, row in filtered_pages.iterrows():
        complexity_scores = json.loads(row['complexity_scores'])
        page_complexity_sum = sum(
            scores[0] for scores in complexity_scores if scores
        )

        magazine_name = magazine_df.loc[magazine_df['id']
                                        == row['magazine_id'], 'name'].values[0]
        magazine_complexity_sums[magazine_name] = (
            magazine_complexity_sums.get(
                magazine_name, 0) + page_complexity_sum
        )

    # Sort magazines based on creation_date
    sorted_magazine_complexity_sums = sorted(magazine_complexity_sums.items(
    ), key=lambda x: magazine_df.loc[magazine_df['name'] == x[0], 'creation_date'].values[0])

    # Extract sorted magazine names and complexity sums
    sorted_labels = [item[0] for item in sorted_magazine_complexity_sums]
    sorted_complexity_sums = [item[1]
                              for item in sorted_magazine_complexity_sums]

    # Create a bar chart
    fig = go.Figure(data=[go.Scatter(
        x=sorted_labels,
        y=sorted_complexity_sums,
        mode='lines+markers',
        text=[s for s in sorted_complexity_sums],
        hoverinfo='x+y',  # show magazine name and complexity score on hover
        line=dict(color='#BF616A'),
        marker=dict(color='#BF616A', size=PLOTLY_MARKER_SIZE)
    )])

    # Update layout for better visualization
    fig.update_layout(
        template="plotly_dark",
        xaxis_title='Tijdschrift',
        yaxis_title='Complexiteitsscore',
        legend_title="Tijdschriften",
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        height=621,
        width=640,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        )
    )

    return Graph(figure=fig)


def create_complexity_v_topic_scatter_plot(selected_magazine_ids):
    if not selected_magazine_ids:
        return P("Nog geen tijdschrift geselecteerd.")

    def extract_complexity_scores(stored_score_info):
        return [score[0] for score in stored_score_info if score]

    data = db.get_table_as_df(db.Page)
    data = data[data['magazine_id'].isin(selected_magazine_ids)]

    data['page_topic'] = data['page_topic'].apply(eval)
    data['complexity_scores'] = data['complexity_scores']\
        .apply(eval)\
        .apply(extract_complexity_scores)
    data['mean_complexity_score'] = data['complexity_scores'].apply(np.mean)

    grouped_data = data.groupby('page_topic').agg(
        mean_complexity_score=('mean_complexity_score', 'mean'),
        # Counting the occurrences of each topic
        topic_count=('page_topic', 'size')
    ).reset_index()

    fig = go.Figure()

    for topic in grouped_data['page_topic']:
        topic_data = grouped_data[grouped_data['page_topic'] == topic]
        fig.add_trace(go.Scatter(
            x=topic_data['mean_complexity_score'],
            y=topic_data['topic_count'],
            mode='markers',
            marker=dict(
                size=PLOTLY_MARKER_SIZE,
                color=topic_color_map.get(topic, '#ff0000')
            ),
            name=topic,
            hoverinfo='text',
            hovertext=[
                (
                    f"Topic: {topic}"
                    f"<br>Mean Complexity: {row['mean_complexity_score']}"
                    f"<br>Count: {row['topic_count']}"
                )
                for _, row in topic_data.iterrows()
            ],
            showlegend=False
        ))

    # Update layout similar to what px.scatter provides
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        height=624,
        width=640,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )

    return Graph(figure=fig)


def create_topic_popularity_graph(selected_topics):
    if not selected_topics:
        return P("Nog geen topics geselecteerd.")

    if type(selected_topics) is str:
        selected_topics = [selected_topics]
    data = db.get_table_as_df(db.Page)
    magazine_data = db.get_table_as_df(db.Magazine)

    data['page_topic'] = data['page_topic'].apply(eval)

    topic_df = pd.merge(
        data,
        magazine_data,
        left_on='magazine_id',
        right_on='id',
        how='inner'
    )
    topic_df['creation_date'] = pd.to_datetime(
        topic_df['creation_date']).dt.year

    fig = go.Figure()

    for topic in selected_topics:

        df_specific_topic = topic_df[topic_df['page_topic'].apply(
            lambda topics: topic in topics)]

        unique_dates = pd.DataFrame(
            topic_df['creation_date'].unique(), columns=['creation_date'])

        count_by_date = df_specific_topic.groupby(
            'creation_date').size().reset_index(name='count')
        result = pd.merge(unique_dates, count_by_date,
                          on='creation_date', how='left').fillna(0)
        result['count'] = result['count'].astype(int)

        result = result.sort_values(by='creation_date')

        hover_text = result.apply(
            lambda row: (
                f"Date: {row['creation_date']}"
                f"<br>Count: {row['count']}"
                f"<br>Topic: {topic}"
            ),
            axis=1
        )

        # Create a bar chart trace
        trace = go.Bar(
            x=result['creation_date'],
            y=result['count'],
            name=topic,
            hoverinfo='text',
            text=hover_text,
            textposition='none',
            marker=dict(color=topic_color_map.get(topic, '#ff0000')),
            showlegend=False
        )
        fig.add_trace(trace)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#3B4252',
        plot_bgcolor='#3B4252',
        height=589,
        width=640,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        xaxis_title='Creation Date',
        yaxis_title='Topic Count',
        barmode='group',
    )

    return Graph(figure=fig)


def register_dashboard_callbacks(app: Dash):
    @app.callback(
        Output('complexity-graph-container', 'children'),
        Input('magazine-dropdown', 'value')
    )
    def update_complexity_graph(selected_magazines):
        return [
            H2('Complexiteit lijn grafiek over tijd:'),
            create_complexity_graph(selected_magazines)
        ]

    @app.callback(
        Output('topic-pie-container', 'children'),
        Input('magazine-dropdown', 'value')
    )
    def update_topic_pie(selected_magazines):
        return [
            H2('ML onderwerp(en):'),
            topic_pie_url(selected_magazines)
        ]

    @app.callback(
        Output('scatter-plot-container', 'children'),
        Input('magazine-dropdown', 'value')
    )
    def update_scatter_plot(selected_magazines):
        return [
            H2('Gemiddelde complexiteit & pagina ml-onderwerp opsomming:'),
            create_complexity_v_topic_scatter_plot(selected_magazines)
        ]

    @app.callback(
        Output('topic-popularity-scatter', 'children'),
        Input('topic-dropdown', 'value')
    )
    def update_topic_pop(selected_topics):
        return [
            create_topic_popularity_graph(selected_topics)
        ]

    @app.callback(
        Output('topic-dropdown', 'value', allow_duplicate=True),
        Input('pie-graph', 'clickData'),
        prevent_initial_call=True
    )
    def display_click_data(clickData):
        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            selected_label = clickData['points'][0]['label'].replace('"', '')
            return selected_label

    @app.callback(
        Output('wordcloud-container', 'children'),
        [
            Input('magazine-dropdown', 'value'),
            Input('magazine_wordcloud_min_font_size', 'value'),
            Input('magazine_wordcloud_max_words', 'value'),
        ]
    )
    def update_magazine_wordcloud(
        selected_magazines,
        min_font_size,
        max_words
    ):
        content = create_magazine_wordcloud_div(
            min_font_size,
            max_words
        )

        content.append(
            create_magazine_word_cloud(
                selected_magazines,
                min_font_size,
                max_words
            )
        )

        return content

    @app.callback(
        Output('topic-cloud-container', 'children'),
        [
            Input('magazine-dropdown', 'value'),
            Input('topic_wordcloud_min_font_size', 'value'),
            Input('topic_wordcloud_max_words', 'value'),
        ]
    )
    def update_topic_wordcloud(
        selected_magazines,
        min_font_size,
        max_words
    ):
        content = create_topic_word_cloud_div(
            min_font_size,
            max_words
        )

        content.append(
            create_topic_word_cloud(
                selected_magazines,
                min_font_size,
                max_words
            )
        )

        return content
