import json
import os
import shutil
import re
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sqlalchemy.orm import Session
from utils import database
from utils.database import DB_ENGINE
from utils.logging import build_logger

from .topic_utils import remove_stopwords_from_text

log = build_logger(__name__)


def load_and_preprocess_data(model_exists: bool):
    """Loads data from the database, preprocesses it for BERTopic.

    Args:
        model_exists: Whether the model already exists or not.

    Returns:
        DataFrame: The preprocessed data.
        docs: A list of strings ready for BERTopic fitting.
    """

    data = database.get_table_as_df(database.Page)

    if model_exists:  # Only load data with null page_topic if the model already exists
        data = data[data['page_topic'].isnull()]

    data['tokenized_text'] = data['tokenized_text']\
        .apply(eval).apply(remove_stopwords_from_text)
    docs = [' '.join(doc) for doc in data['tokenized_text']]
    return data, docs


def train_topic_model(docs: list):
    hdbscan_model = HDBSCAN(
        min_cluster_size=8,
        prediction_data=True
    )

    topic_model = BERTopic(
        language="multilingual",
        hdbscan_model=hdbscan_model,
        verbose=True
    )

    topic_model.fit(docs)

    shutil.rmtree('models/page_model', True)
    os.makedirs('models/page_model', exist_ok=True)
    topic_model.save(
        'models/page_model',
        serialization="safetensors",
        save_ctfidf=True
    )

    return topic_model


def run(override_existing: bool = False):
    """Main function to orchestrate the topic modeling process."""
    model_exists = os.path.exists('models/page_model')

    data, docs = load_and_preprocess_data(
        model_exists and not override_existing
    )

    if model_exists and not override_existing:
        log.info('Loading existing page model...')
        topic_model = BERTopic.load('models/page_model')
    else:
        log.info('Training page model...')
        topic_model = train_topic_model(docs)
        log.info('Model trained and saved.')

    log.info('Applying topic model...')
    topics, _ = topic_model.transform(docs)

    topics = topic_model.reduce_outliers(docs,
                                         topics,
                                         strategy="c-tf-idf",
                                         threshold=0.1)

    topic_info = topic_model.get_topic_info()
    topic_label = []
    for topic in topics:
        topic_word = topic_info[topic_info['Topic'] == topic]['Name'].values[0]
        topic_word = (re.sub(r'^\d+_', '', topic_word)
                      .replace('_', '-')
                      .replace('-1', 'unknown'))
        topic_label.append(topic_word)

    log.info(f'Topics generated: {len(set(topic_label))}')

    data['topic_string'] = topic_label

    with Session(DB_ENGINE) as session:
        for __, row in data.iterrows():
            db = session.query(database.Page).filter_by(id=row['id']).first()
            if db:
                db.page_topic = json.dumps(row['topic_string'])
        session.commit()

    log.info('Topic modeling complete.')
