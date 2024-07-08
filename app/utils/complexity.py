"""
machine_learning.py
This file is responsible for calculating the complexity score for each page of the magazine.
The complexity score is calculated by the terms (reductive or complex) defined by the user.
"""
from . import database as db


def calc_complexity(session, split_text):
    # Extract words from the database based on antonym status
    antonyms = {word.word for word in session.query(db.WordObject.word).filter(db.WordObject.type == 3)}

    # Get all WordObjects from database for counting
    reductionistic_words = {word.word: {'gewicht': word.weight, 'frequentie': 0} for word in
                            session.query(db.WordObject).filter(db.WordObject.type == 1)}
    complex_words = {word.word: {'gewicht': word.weight, 'frequentie': 0} for word in
                     session.query(db.WordObject).filter(db.WordObject.type == 2)}

    # Calculate reductionistic and complex count scores
    complex_count = 0
    reductionistic_count = 0

    for i in range(1, len(split_text)):
        current_word = split_text[i]
        previous_word = split_text[i - 1] if i > 0 else None

        # check word if it exists in reductionistic words
        if current_word in reductionistic_words:
            gewicht = reductionistic_words[current_word]['gewicht']

            if gewicht > 0:
                if previous_word in antonyms:
                    complex_count += gewicht
                else:
                    reductionistic_count += gewicht

                reductionistic_words[current_word]['frequentie'] += 1

        # check word if it exists in complex words
        elif current_word in complex_words:
            gewicht = complex_words[current_word]['gewicht']

            if gewicht > 0:
                if previous_word in antonyms:
                    reductionistic_count += gewicht
                else:
                    complex_count += gewicht

                complex_words[current_word]['frequentie'] += 1

    # Filter out words with frequency = 0
    filtered_word_frequencies = {
        word: {'frequentie': data['frequentie'], 'gewicht': data['gewicht']}
        for word, data in {**reductionistic_words, **complex_words}.items()
        if data['frequentie'] > 0
    }

    # Calculate complexity score: difference between counts of complex and reductionistic words
    complexity_score = complex_count - reductionistic_count

    return int(complexity_score), filtered_word_frequencies
