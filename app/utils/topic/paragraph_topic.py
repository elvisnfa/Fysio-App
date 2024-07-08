import json
import os
import shutil
import re
from umap import UMAP
from bertopic import BERTopic
from hdbscan import HDBSCAN
from pandas import DataFrame
from sqlalchemy.orm import Session
from utils.database import DB_ENGINE, Page, get_table_as_df
from utils.logging import build_logger

from .topic_utils import remove_stopwords_from_text

log = build_logger(__name__)


def load_and_run_par_model(data):
    """
    Loads a pre-trained model, transforms paragraph data, and labels topics.
    """
    log.info('load & run paragraph model')
    data = data[data['par_topics'].isnull()]
    return BERTopic.load('models/paragraph_model'), parse_str_data(data), data


def train_and_run_par_model(data: DataFrame):
    """
    Trains a new model, transforms paragraph data, and labels topics.
    """
    log.info('running paragraph model')

    str_data = parse_str_data(data)

    hdbscan_model = HDBSCAN(
        min_cluster_size=60,
        prediction_data=True
    )

    topic_model = BERTopic(
        language="multilingual",
        hdbscan_model=hdbscan_model,
        top_n_words=10,
        verbose=True
    )
    topic_model.fit(str_data)

    shutil.rmtree('models/paragraph_model', True)
    os.makedirs('models/paragraph_model', exist_ok=True)

    topic_model.save(
        'models/paragraph_model',
        serialization="safetensors"
    )

    return topic_model, str_data


def results_par(data: DataFrame, topic_label, topics):
    """
    This function handles paragraph-level topic labeling and database updates.
    """
    total_paragraphs = sum(
        len(row['tokenized_text']) for _, row in data.iterrows()
    )
    if len(topics) < total_paragraphs:
        raise ValueError("topic & paragraph index not matching")

    with Session(DB_ENGINE) as session:
        topic_idx = 0
        for _, row in data.iterrows():
            row_list = []
            for _ in row['tokenized_text']:
                row_list.append(topic_label[topic_idx])
                topic_idx += 1

            stored_page = (
                session
                .query(Page)
                .filter_by(id=row['id'])
                .first()
            )
            if stored_page:
                stored_page.par_topics = json.dumps(row_list)

        session.commit()


def parse_str_data(data: DataFrame):
    return [par for row in data['tokenized_text'] for par in row]


def run(override_existing: bool = False):
    """
    Main function to orchestrate topic modeling process for paragraphs.
    """
    data = get_table_as_df(Page)

    data['tokenized_text'] = \
        data['tokenized_text'].apply(eval).apply(remove_stopwords_from_text)

    if os.path.exists('models/paragraph_model') and not override_existing:
        topic_model, str_data, data = load_and_run_par_model(data)
    else:
        topic_model, str_data = train_and_run_par_model(data)

    topics, __ = topic_model.transform(str_data)

    # topics = topic_model.reduce_outliers(str_data,
    #                                      topics,
    #                                      strategy="c-tf-idf",
    #                                      threshold=0.1)

    topic_info = topic_model.get_topic_info()
    topic_label = []
    for topic in topics:
        topic_word = topic_info[topic_info['Topic'] == topic]['Name'].values[0]
        topic_word = re.sub(r'^\d+_', '', topic_word).replace('_', '-').replace('-1', 'unknown')
        topic_label.append(topic_word)

    log.info(f'Topics generated: {len(set(topic_label))}')

    results_par(data, topic_label, topics)
