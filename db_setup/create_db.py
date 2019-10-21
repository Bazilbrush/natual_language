import sqlite3
from db_setup import databaseconfig as database

db = sqlite3.connect(database.database)
# create the tables
cursor = db.cursor()

# main tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_index(fileid INTEGER PRIMARY KEY AUTOINCREMENT, 
    filename TEXT, filepath TEXT, subject TEXT)
    ''')
db.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags(tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fileid INTEGER NOT NULL, tag TEXT,source TEXT, weight REAL,
    FOREIGN KEY (fileid) REFERENCES search_index(fileid))
    ''')
db.commit()

cursor.execute('''
    CREATE TABLE word_jargon(word TEXT primary key UNIQUE, token TEXT, weight REAL)
    ''')
db.commit()

db.close()