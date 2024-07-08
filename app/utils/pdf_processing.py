import hashlib
import re
from io import BytesIO

import chardet
import pandas as pd
from dateutil import parser as pars
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTChar, LTFigure, LTTextBoxHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from unidecode import unidecode
from utils.logging import build_logger

pd.set_option('display.max_colwidth', None)

log = build_logger(__name__)


def extract_text_pdf(stream: BytesIO):
    stream.seek(0)
    parser = PDFParser(stream)
    document = PDFDocument(parser)

    if not document.is_extractable:
        log.error('Unable to extract text.')
        raise PDFTextExtractionNotAllowed

    text_list = []
    laparams = LAParams()

    for page_layout in extract_pages(stream, laparams=laparams):
        column_text = []
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                column_text.append(element.get_text())

            elif isinstance(element, LTFigure):
                figure_text = process_figure(element)
                column_text.append(figure_text)

        text_list.append(column_text)

    return text_list


def process_figure(figure):
    # Extract LTChar elements from the figure
    chars = [char for char in figure if isinstance(char, LTChar)]
    if not chars:
        return ''

    # Group characters into words
    words = group_chars_into_words(chars)
    # Group words into lines
    lines = group_words_into_lines(words)

    # Combine lines into a single string
    figure_text = '\n'.join(
        [' '.join([word['text'] for word in line]) for line in lines]
    )
    return figure_text


def group_chars_into_words(chars):
    words = []
    current_word = []
    prev_char = None

    for char in chars:
        if prev_char:
            if char.x0 - prev_char.x1 > 1:  # Simple space threshold
                if current_word:
                    word_text = ''.join([c.get_text() for c in current_word])
                    words.append(
                        {'text': word_text,
                            'x0': current_word[0].x0, 'x1': current_word[-1].x1}
                    )
                    current_word = []
        current_word.append(char)
        prev_char = char

    if current_word:
        word_text = ''.join([c.get_text() for c in current_word])
        words.append(
            {'text': word_text,
                'x0': current_word[0].x0, 'x1': current_word[-1].x1}
        )

    return words


def group_words_into_lines(words):
    lines = []
    current_line = []
    prev_word = None

    for word in words:
        if prev_word:
            if word['x0'] - prev_word['x1'] > 10:  # Simple new line threshold
                if current_line:
                    lines.append(current_line)
                    current_line = []
        current_line.append(word)
        prev_word = word

    if current_line:
        lines.append(current_line)

    return lines


def extract_metadata_pdf(stream: BytesIO):
    stream.seek(0)
    parser = PDFParser(stream)

    document = PDFDocument(parser)
    metadata = document.info[0]

    final_metadata = {}

    for key, value in metadata.items():
        if isinstance(value, bytes):
            encoding = chardet.detect(value)['encoding']
            if encoding is None:
                encoding = 'utf-8'

            decoded_value = value.decode(encoding)
        else:
            decoded_value = value

        final_metadata[key] = decoded_value

    if 'CreationDate' in final_metadata and len(final_metadata['CreationDate']) > 2:
        date_string = final_metadata['CreationDate'][2:]
        date_string = date_string.split('+')
        date_string = date_string[0]

        dt = pars.parse(date_string)
        final_metadata['CreationDate'] = dt

    return final_metadata


def generate_file_hash(stream: BytesIO):
    """Hashes an pdf file """

    stream.seek(0)
    hash = hashlib.md5(stream.read()).hexdigest()

    return hash


def extraction(stream: BytesIO):
    stream.seek(0)

    df = pd.DataFrame({"Page Text": extract_text_pdf(stream)})
    df['Page Text'] = df['Page Text'].apply(remove_meta_chars)
    df['split_text'] = df['Page Text'].apply(split_paragraph).apply(clean_data)

    return df


def clean_data(page_text):
    bad_chars = (',', '.', '!', '?', ':', '"', '(', ')', '')
    cleaned_page_text = []
    numeric_regex = re.compile(r'\b\d+\b')
    merge_next_word = False
    next_word = ''

    for paragraph in page_text:
        cleaned_paragraph = []

        # Cleaning separate words
        for word in paragraph:

            # Word level cleaning
            word = word.lower()
            word = unidecode(word)

            # Remove all numeric words
            if numeric_regex.search(word):
                continue

            # Remove/skip over words containing 'www' or '@' (to remove website links or emails)
            if 'www' in word or '@' in word:
                continue

            # Remove apostrophe from the beginning of the words (bug fix)
            if word.startswith("'") and not word.endswith("'"):
                word = word[1:]

            # Remove apostrophe from the end of the words (bug fix)
            if word.endswith("'") and not word.startswith("'"):
                word = word[:-1]

            # Loop over every character in a word to check if it is in bad_chars
            cleaned_word = ''.join(
                char for char in word if char not in bad_chars
            )

            if merge_next_word:
                # If the current word ends with a hyphen, merge with the current word
                cleaned_word = next_word + cleaned_word
                # Reset to false for following merges
                merge_next_word = False
            # Skip/remove all single character values
            elif len(cleaned_word) == 1:
                continue

            # If the current word ends with a hyphen, prepare to merge with the next word
            if word.endswith('-'):
                # Store the word fragment without the hyphen
                next_word = cleaned_word[:-1]
                merge_next_word = True
            else:
                # Only append non-empty words
                if cleaned_word:
                    cleaned_paragraph.append(cleaned_word)

        if cleaned_paragraph:
            cleaned_page_text.append(cleaned_paragraph)

    return cleaned_page_text


def remove_meta_chars(list):
    string_list = []

    for element in list:
        text = ''
        if type(element) is not str:
            element = element.get_text()

        text = element.replace('\n', ' ').replace('\t', ' ')
        string_list.append(text)

    return string_list


def split_paragraph(string_list):
    split_list = []

    for paragraph in string_list:
        split_list.append(list(paragraph.split()))

    return split_list
