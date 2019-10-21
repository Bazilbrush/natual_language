import sqlite3
from functools import reduce
import searchlib as lib
from db_setup import databaseconfig as database


# create the db connection and cursor
db = sqlite3.connect(database.database)
cursor = db.cursor()


def generate_init_weights():

    list_tags(list_objects())

    # get distinct groups of tags CODE DUPLICATION!!!!!!
    cursor.execute('''SELECT DISTINCT fileid from tags''')
    db.commit()
    object_list = cursor.fetchall()
    object_list = [list(obj) for obj in object_list]
    object_list = reduce(lambda x, y: x + y, object_list)
    # loop over the objects and scale the weight values for each object to add up to 1
    for obj in object_list:
        cursor.execute('''SELECT tag_id, weight FROM tags WHERE fileid=?''', (obj,))
        db.commit()
        tag_ids = cursor.fetchall()
        weight_list = []
        tag_id_list = []
        [weight_list.append(row[1]) for row in tag_ids]
        [tag_id_list.append(row[0]) for row in tag_ids]

        new_weights = lib.scale_values(weight_list)

        weight_id_iterable = dict(zip(tag_id_list, new_weights))

        for tag_id, nw in weight_id_iterable.items():

            cursor.execute('''UPDATE tags SET weight = ? where fileid = ? and tag_id =? ''', (nw, obj, tag_id))
            db.commit()


def list_objects():
    # get a list of objects in the search index
    cursor.execute('''SELECT fileid FROM search_index''')
    db.commit()

    object_list = cursor.fetchall()

    # get rid of tuples because tuples are stupid
    object_list = [list(obj) for obj in object_list]
    object_list = reduce(lambda x, y: x+y, object_list)

    return object_list


def list_tags(object_list):
    # for each object get a list of tags
    for obj in object_list:
        cursor.execute('''SELECT tag FROM tags WHERE fileid=?''', (int(obj),))
        db.commit()
        tag_list = cursor.fetchall()
        tag_list = [list(tag) for tag in tag_list]
        try:
            tag_list = reduce(lambda x, y: x+y, tag_list)

        except TypeError:
            print("empty")

        update_weights(tag_list)


def update_weights(tag_list):
    # if tag is 'special' copy weight from ons_jargon as baseline, otherwise add baseline weight
    for tag in tag_list:
        cursor.execute('''SELECT 1 FROM ons_jargon WHERE word = ?''', (tag, ))
        db.commit()
        flag = cursor.fetchone()
        if flag is None:
            cursor.execute('''UPDATE tags SET weight = 0.5 WHERE tag = ?''', (tag, ))
            db.commit()
        else:
            cursor.execute('''UPDATE tags SET weight = (SELECT weight FROM ons_jargon WHERE word = ? )
                WHERE tag = ?''', (tag, tag, ))
            db.commit()


