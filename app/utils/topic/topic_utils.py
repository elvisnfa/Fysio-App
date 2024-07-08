
from utils.database import BadWord, get_table_as_df


def remove_stopwords_from_text(text):
    stopwords = set(get_table_as_df(BadWord)['word'].to_list())

    return [
        ' '.join([
            word
            for word in paragraph
            if word.strip() not in stopwords
        ])
        for paragraph in text
    ]
