# session_tunes.py
# Author: Dallin Nielson
# Code for scraping data for tunes on thesession.org

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


def set_display_options():

    """
    Sets the display options for working with the pandas DataFrame data
    """

    pd.set_option('display.width', 150)
    pd.set_option('display.max_colwidth', 20)
    pd.set_option('display.max_columns', None)


def get_soup(tune_id):

    """
    Looks up a tune on thesession.org and returns a BeautifulSoup object
    from its webpage.

    :param tune_id: the id of the tune to search for
    :return: a BeautifulSoup object for the tune on thesession.org
    """

    tunes_url = r'https://thesession.org/tunes/'

    attempts = 0
    awaiting_response = True
    while awaiting_response and attempts < 2:
        try:
            r = requests.get(tunes_url + str(tune_id))
            awaiting_response = False
        except:
            attempts += 1

    # If there is an error with the HTTP response, raise an error
    try:
        r.raise_for_status()
    except:
        raise requests.HTTPError

    soup = BeautifulSoup(r.text, 'html.parser')

    return soup


def get_session_tunes(pages, start=1, library=None):

    """
    Iterates over many tune pages on thesession.org and compiles the
    information from all the discovered tunes into a list of dictionaries,
    where each dictionary contains information about 1 tune.

    :param pages: The number of pages to iterate over on thesession.org
    :param start: The starting point for the iteration
    :param library: An optional list of previously compiled tunes
    :return: a list of dictionaries with information about each tune that
        was discovered on thesession.org.
    """

    # If library is provided, ensure it is a valid 1D list and set the
    # tune_list equal to the existing library. Otherwise, start a new
    # list for the tune_list output.
    if library is not None:
        try:
            assert type(library) == list
            tune_list = library
        except AssertionError:
            raise AssertionError("library must be a 1D list.")
    else:
        tune_list = []

    # Iterate over each page in the sequence that was specified
    for num in range(start, start + pages):

        # Try to get the response and create the bs4 soup.
        # If there is an error with the HTTP response, skip the iteration
        try:
            soup = get_soup(num)
        except requests.HTTPError:
            continue

        # Get the compiled info from the soup and append it to the tune_list
        strained_soup = strain_soup(soup, num)
        tune_list.append(strained_soup)

    id_range = f'{start}-{start + pages - 1}'
    print(f'Obtained data for {len(tune_list)} tunes (IDs {id_range}).')
    return tune_list


def strain_soup(soup, tune_id):
    """
    Parses HTML from a tune at thesession.org and returns its information.

    :param soup: A BeautifulSoup object
    :param tune_id: integer representing the ID of the tune on the website
    :return: a dictionary with information about the tune
    """

    # Run the functions that parse the soup to retrieve the data from its
    # elements
    tune_type, tune_name = parse_h1(soup)
    recordings = parse_summary(soup)
    recorded_with = parse_stats(soup)
    aliases, collections, tune_sets, tune_books = parse_paragraphs(soup)
    tabs = parse_tabs(soup)

    # Create the dictionary with the final output
    strained_soup = {
        "id": tune_id,                  # the tune ID
        "name": tune_name,              # the name of the tune
        "aliases": aliases,             # alternative names for the tune
        "type": tune_type,              # the genre of the tune
        "set_pairings": recorded_with,  # ids of common tune pairings
        "tabs": tabs,                   # the number of tabs for the tune
        "recordings": recordings,       # the number of recordings
        "collections": collections,     # the number of collections
        "sets": tune_sets,              # the number of sets
        "books": tune_books,            # the number of tune books
    }

    return strained_soup


def parse_h1(soup_obj):
    """
    Takes a bs4.BeautifulSoup object representing a tunes page from
    thesession.org and returns the tune type and name from the H1 heading

    :param soup_obj: a BeautifulSoup object
    :return: a tuple containing 1. the tune type and 2. the tune name
    """

    # Find the H1 heading, or return empty content if it isn't found
    try:
        h1 = soup_obj.find('h1')
    except:
        return 'H1 Error', 'H1 Error'

    # Get the Tune Type
    try:
        tune_type = h1.find('a').text
    except:
        tune_type = 'Error'

    # Get the name of the tune
    try:
        tune_name = h1.text.rstrip(tune_type).rstrip(' ')
    except:
        tune_name = 'Error'

    return tune_type, tune_name


def parse_paragraphs(soup_obj):

    """
    Parses the first <p> elements from the <main> section

    :param soup_obj: a bs4 BeautifulSoup object for a thesession.org tune
    :return: a tuple with 4 values, containing the following values:
        aliases: a string containing alternate names for the tune
        collections: an integer with the count of collections the tune
            is part of
        tune_sets: the number of tune sets the tune has been added to
        tune_books: the number of books that the tune belongs to
    """

    # Attempt to extract alternate names (aka aliases) for the tune
    try:
        aliases_elem = soup_obj.find('p', attrs={'class': 'info'})
        aliases = aliases_elem.text.replace('Also known as\n', '')
    except:
        aliases = ""

    # Attempt to extract the number of collections the tune is a part of
    try:
        collection_regex = re.compile(
            '[\d,]+ other tune collections', re.IGNORECASE)

        collections_text = soup_obj.find('a', string=collection_regex).text
        collections = parse_count(collections_text)
    except:
        collections = 0

    # Attempt to extract the number of tune sets the tune has been added to
    try:
        # tune_sets = parse_count(paragraphs[2].text)

        tune_sets_regex = re.compile('[\d,] tune sets', re.IGNORECASE)

        tune_sets_text = soup_obj.find('a', string=tune_sets_regex).text
        tune_sets = parse_count(tune_sets_text)
    except:
        tune_sets = 0

    # Attempt to extract the number of tune books the tune has been added to
    try:
        tune_book_regex = re.compile(
            'has been added to [\d,]+ tunebooks', re.IGNORECASE)

        tune_book_text = soup_obj.find('p', string=tune_book_regex).text
        tune_books = parse_count(tune_book_text)
    except:
        tune_books = 0

    return aliases, collections, tune_sets, tune_books


def parse_summary(soup_obj):
    """
    Extracts the number of times the tune has been recorded

    :param soup_obj: a bs4 BeautifulSoup object for a thesession.org tune
    :return: An integer for the number of times the tune has been recorded
    """

    # Attempt to extract the <summary> elem from the soup object
    try:
        summary = soup_obj.find('details').find('summary')
    except:
        return 0

    # Attempt to extract the Recordings list from the summary
    try:
        recordings = parse_count(summary.find('a').text)
        return recordings
    except:
        return 0


def parse_stats(soup_obj):
    """
    Extracts the 'data-tuneid' from the <a> element for each tune that
    is listed under the class='stats' section of the soup_obj

    :param soup_obj: a bs4 Beautiful Soup object for a thesession.org tune
    :return: a 1D array of integers for the IDs of tunes that are commonly
        recording along with the tune in the soup_obj
    """

    # Attempt to extract the tunes that are commonly recorded with the
    # tune in the soup_obj
    try:
        return [int(tune['data-tuneid']) for tune in
                     soup_obj.find(class_='stats').findAll('a')]
    except (TypeError, AttributeError):
        return None


def parse_tabs(soup_obj):

    """
    Counts the number of tabs (aka. sheet music tabs) on the page

    :param soup_obj: a BeautifulSoup object for a thesession.org tune
    :return: and integer for the number of tabs on the page
    """

    try:
        tabs = soup_obj.findAll('div', attrs={'class': 'setting-sheetmusic'})
    except:
        tabs = []

    return len(tabs)


def parse_count(text):

    """
    Parses a string of text and returns an integer with the first number
    string of any length encountered in the text.

    :param text: a string of text
    :return: an integer, or None if no number was found in the text
    """

    try:
        num_string = re.search('[\d,]+', text).group()
        num = int(num_string.replace(',', ''))
        return num

    except (ValueError, AttributeError):
        return None


def main():

    """
    Creates equal sized batches, then runs get_session_tunes for each batch
    and combines the new tunes with the existing tunes in 'tunes.json', then
    saves the combined data to 'tunes.json'
    """

    number_tunes = 24000
    batch_size = 250
    starting_point = 1

    batches = list(range(starting_point, number_tunes, batch_size))

    for batch in batches:

        # run get_session_tunes on the tune id's in the batch
        new_df = pd.DataFrame(get_session_tunes(batch_size, start=batch))
        indexed_df = new_df.set_index('id')

        # Import existing tunes from the tunes.json library and combine the
        # new tunes with the existing library
        library = pd.read_json('tunes.json')
        combined_data = pd.concat([library, indexed_df])

        # Save the combined data to tunes.json
        combined_data.to_json('tunes.json')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()