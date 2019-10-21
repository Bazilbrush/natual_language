import sqlite3
import os
import nltk
from nltk.corpus import wordnet
from string import punctuation
from db_setup import databaseconfig as database


# create db connection
db = sqlite3.connect(database.database)


# find files - for now we're looking at text files in a specific directory, later we will have to write a scraper
def find_files():
    # search term is not used. yet... and probably never will be
    path = 'C:/Users/bazilj/PycharmProjects/nltk_test/text_samples'

    file_list = os.listdir(path)

    return file_list


# check database if record exists in the index, return a full line
def get_records_from_index(file, db):
    # check in db for the file
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM search_index WHERE filename=? ''', (file,))
    record = cursor.fetchone()
    db.commit()
    # check for nulls and replace - consider refactoring
    if record is None:
        record = ['None', 'None']
    return record


# tokenize text
def tokenize(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    return text


# compare the current tag list to known jargon; correct the tag if required
def jargon_lookup(tag_list, db):
    # init counter
    i = 0
    for tag in tag_list:
        # convert to list
        tag = list(tag)
        cursor = db.cursor()
        cursor.execute('''SELECT token FROM ons_jargon WHERE word=? ''', (tag[0],))
        token = cursor.fetchone()
        if token is None:
            pass
        else:
            tag[1] = token[0]

        tag_list[i] = tag
        i += 1
    return tag_list


# add the tags to the table
def insert_tag(file, tag, source, db, weight):
    # we need the file id to keep constraints
    fileid = get_records_from_index(file, db)[0]
    # check for duplicates and insert tags
    cursor = db.cursor()
    cursor.execute('''SELECT tag FROM tags where fileid=? and source=? and tag=? ''', (int(fileid), source, tag[0]))
    db.commit()
    if cursor.fetchone() is None:
        cursor = db.cursor()
        cursor.execute('''INSERT OR REPLACE INTO tags(fileid, tag, source, weight)
                        VALUES(?,?,?,?)
                         ''', (int(fileid), tag, source, weight))
        db.commit()


# scale a list of values so they all add up to 1
# used in weight generation
def scale_values(value_list):
    list_sum = sum(value_list)
    scaled_list = [val/list_sum for val in value_list]
    return scaled_list


# generate prevailing subject based on tag and their weight; will be moved to a separate module after
def get_subject():

    cursor = db.cursor()
    # get number of files in index (consider extracting a list if we going to have issues with consistency
    cursor.execute('''SELECT MAX(fileid) FROM search_index''')
    db.commit()
    ids = cursor.fetchone()[0]

    # for each file
    for i in range(1, ids+1):
        # get tags and weights
        cursor.execute('''SELECT tag, weight FROM tags where fileid = ? ''', (i,))
        db.commit()
        tags = cursor.fetchall()
        try:
            # find largest weight > thus the most relevant tag
            max_val = max(dict(tags).values())

            # put corresponding tag into the subject
            subject = list(dict(tags).keys())[list(dict(tags).values()).index(max_val)]
            cursor.execute('''UPDATE search_index SET subject=? where fileid=?''', (subject, i))
            db.commit()
        except ValueError:
            print("empty tags")


def clean_text(text):
    lower_case = text.lower()
    remove = punctuation
    # remove punctuation - for some reason the nice method of just calling string.punctuation in the translate
    # produces garbage. :S
    # custom punctuation table: we want to keep the dashes and underscores
    remove = remove.replace("_", "")
    remove = remove.replace("-", "")
    no_punctuation = lower_case.translate({ord(char): None for char in remove})

    # we want to get rid of lonely numbers and letters; consider changing to 2 rather than 3
    no_singletons = ' '.join(word for word in no_punctuation.split() if len(word) > 3)
    return no_singletons


# this function turns Treebank Part Of Speech tags into ones usable by wordnet lemmatizer
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN
