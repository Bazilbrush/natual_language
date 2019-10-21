import sqlite3
from db_setup import databaseconfig as database

# initial weight of each keyword - subject to change
weight = 0.7

# list of special words
specials = [
    ['val', 'NN'],
    ['vul', 'NN'],
    ['word', 'NN'],
    ['word1', 'NN'],
    ['word2', 'NN']
]

# populate ons_jargon table which stores special words and terms that we need to flag

db = sqlite3.connect(database.database)

cursor = db.cursor()

for i in range(0 , len(specials)-1):
    cursor.execute('''INSERT OR REPLACE INTO words_jargon(word, token, weight)
                        VALUES(?,?,?)
                         ''', (specials[i][0], specials[i][1], weight),)
    db.commit()

