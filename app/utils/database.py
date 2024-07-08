import json
import os
import sys

import pandas as pd
from nltk.corpus import stopwords
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        create_engine)
from sqlalchemy.orm import Session, declarative_base, relationship
from utils.logging import build_logger

DB_ENGINE = create_engine('sqlite:///bigdata.db')


log = build_logger(__name__)


SQLAlchemyBaseClass = declarative_base()


class Magazine(SQLAlchemyBaseClass):
    __tablename__ = 'Magazine'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    hash = Column(String)
    creation_date = Column(DateTime)
    pages = relationship(
        "Page",
        back_populates="magazine",
        cascade="all"
    )


class Page(SQLAlchemyBaseClass):
    __tablename__ = 'Page'

    id = Column(Integer, primary_key=True, autoincrement=True)
    magazine_id = Column(Integer, ForeignKey('Magazine.id'))
    raw_text = Column(Text)
    page_text = Column(Text)
    tokenized_text = Column(Text)
    complexity_scores = Column(Text)
    page_topic = Column(Text)
    par_topics = Column(Text)

    magazine = relationship(
        "Magazine",
        back_populates="pages"
    )


# team 1 model
class WordObject(SQLAlchemyBaseClass):
    __tablename__ = 'Wordlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True)
    type = Column(String)  # reductionistic = 1, complex = 2, antonym = 3
    weight = Column(Integer)


class BadWord(SQLAlchemyBaseClass):
    __tablename__ = 'BadWord'
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True)


SQLAlchemyBaseClass.metadata.create_all(DB_ENGINE)


def init_db(debug: bool):
    with Session(DB_ENGINE) as session:
        if session.query(BadWord).first() is None:
            wordlist = [{"word": word} for word in stopwords.words('dutch')] \
                + load_word_data('assets' + os.sep + 'badwordlist.json', debug)
            insert_first_badwords(wordlist)

        if session.query(WordObject).first() is None:
            wordlist = load_word_data('assets' + os.sep + 'wordlist.json', debug)
            insert_first_wordlist(wordlist)


def add_magazine(df, hash, metadata, filename):
    from utils.complexity import calc_complexity

    with Session(DB_ENGINE) as session:
        # magazine table append model
        new_magazine = Magazine(
            name=os.path.basename(filename),
            hash=hash,
            creation_date=metadata.get('CreationDate', None)
        )

        session.add(new_magazine)

        badwords = [bw.word for bw in session.query(BadWord).all()]

        # setup voor page table append
        for _, row in df.iterrows():
            complexity_list = []

            # complexity score calculation
            for paragraph in row['split_text']:
                score = calc_complexity(session, paragraph)
                complexity_list.append(score)

            # convert data for sqlite compatibility
            raw_text_json = json.dumps(row['Page Text'])
            page_text_json = json.dumps(row['split_text'])

            filtered_split_text = [
                [word for word in paragraph if word not in badwords] for paragraph in row['split_text']]

            tokenized_text_json = json.dumps(filtered_split_text)
            score_json = json.dumps(complexity_list)

            # page table append
            new_page = Page(
                magazine=new_magazine,
                raw_text=raw_text_json,
                page_text=page_text_json,
                tokenized_text=tokenized_text_json,
                complexity_scores=score_json
            )

            session.add(new_page)

        session.commit()


def recalculate_complexity_for_all_magazines():
    from utils.complexity import calc_complexity

    with Session(DB_ENGINE) as session:
        # Query all existing pages of all magazines
        pages = session.query(Page).all()

        # Recalculate complexity for each page
        for page in pages:
            split_text = json.loads(page.page_text)

            page.complexity_scores = json.dumps([
                calc_complexity(session, paragraph)
                for paragraph in split_text
            ])

        # Commit all changes to the database
        session.commit()


def get_table_as_df(table):
    return pd.read_sql_table(table.__tablename__, DB_ENGINE)


def delete_row(table, row):
    with Session(DB_ENGINE) as session:
        object = session.query(table).filter_by(id=row).first()
        if object is not None:
            session.delete(object)
            session.commit()
        else:
            log.info('row not found')


def insert_first_wordlist(wordlist):
    with Session(DB_ENGINE) as session:
        for data in wordlist:
            first_list = WordObject(
                word=data['word'],
                type=data['type'],
                weight=data['weight'])

            session.add(first_list)
        session.commit()


def insert_first_badwords(badwords):
    with Session(DB_ENGINE) as session:
        for data in badwords:
            badword = BadWord(
                word=data['word'],
            )

            session.add(badword)
        session.commit()


def load_word_data(json_file_location, debug: bool):
    with open(json_file_location if debug else resource_path(json_file_location), 'r') as f:
        data = json.load(f)
    return data['words_data']


def resource_path(path):
    """
    Determine the base path for the application.
    If the application is packaged with PyInstaller, '_MEIPASS' will be an attribute of 'sys'.
    This attribute provides the temporary folder created by PyInstaller that contains the extracted files.
    """
    base_path = getattr(
        # The 'sys' module, which contains system-specific parameters and functions.
        sys,
        # The attribute that PyInstaller adds when the app is packaged.
        '_MEIPASS',
        # Default value if '_MEIPASS' is not found.
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # This is the main app directory
    )
    # Join the base path with the provided relative path to get the absolute path.
    return os.path.join(base_path, path)
