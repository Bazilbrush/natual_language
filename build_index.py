import sqlite3
import os
import re
import nltk
import searchlib as lib
import generate_weights as gw
from db_setup import databaseconfig as database

# connect to db at the top
db = sqlite3.connect(database.database)


# main method
def build_index():
    x = lib.find_files()

    insert_file_lists(x)

    gw.generate_init_weights()


# populate tables with file names
def insert_file_lists(file_list):

    for file in file_list:
        # perhaps add a module to get paths?
        path = 'C:/Users/bazilj/PycharmProjects/nltk_test/text_samples'
        absolute_path = path+'/'+file
        # check if inserting duplicates
        if file != lib.get_records_from_index(file, db)[1]:
            cursor = db.cursor()
            cursor.execute('''INSERT INTO search_index(filename, filepath)
                        VALUES(?,?) ''', (file, absolute_path))
            db.commit()
        # perform a filename scan and populate tags
        scan_and_populate_tag(file, db)
    db.close()


# first pass to get tag from file name
def scan_and_populate_tag(file, db):
    # CRUTCH - pop original filename into another var for later use
    orig_filename = file
    # remove extension
    file = os.path.splitext(file)[0]
    # get rid of non-alphanumeric stuff
    file = re.sub(r'[^\w]|_|^\s',  ' ', file)
    # generate tags from the file name
    tagged = nltk.pos_tag(lib.tokenize(file))
    # compare against known ONS tags
    modified_tags = lib.jargon_lookup(tagged, db)
    # first scan tags we only care about nouns and 'special' words
    tags_to_insert = []
    for tag in modified_tags:
        if tag[1] == 'NN' or tag[1] == 'SPECIAL':
            tags_to_insert.append(tag)

    # insert the tags to db
    for tag in tags_to_insert:
        lib.insert_tag(orig_filename, tag[0], 'filename', db, 0)


build_index()






