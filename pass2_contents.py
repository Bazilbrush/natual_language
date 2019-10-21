import sqlite3
from functools import reduce
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
import searchlib as lib
from db_setup import databaseconfig as database

# this pass we create tags for the contents of the file using TF-IDF method

# get the list of files
file_list = lib.find_files()

# probably temporary
path = 'C:/Users/bazilj/PycharmProjects/nltk_test/text_samples'
# consider moving this line somewhere else
db = sqlite3.connect(database.database)


# we need to init the token dictionary where we store the {filename: token1, token2}
token_dict = {}
# set up the stemmer ( stemmer tries to work out the 'stem' of the word, e.g. 'running' -> 'run' )
#stemmer = PorterStemmer()
lemma = nltk.wordnet.WordNetLemmatizer()

def stem_tokens(tokens, lemma):
    #stemmed = []
    lemmatised =[]
    for item in tokens:
        # adding the POS tag makes lemmer more precise as it defaults to noun otherwise
        lemmatised.append(lemma.lemmatize(item, lib.get_wordnet_pos(nltk.pos_tag(nltk.word_tokenize(item))[0][1])))
        #stemmed.append(stemmer.stem(item))
    #return stemmed
    return lemmatised


# yes, there's another tokenizer in my 'common' library file
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, lemma)
    return stems


def normalize_tokens():

    cursor = db.cursor()
    cursor.execute('''SELECT distinct fileid from tags''')
    db.commit()
    file_id_list = cursor.fetchall()

    file_id_list = [list(obj) for obj in file_id_list]
    file_id_list = reduce(lambda x, y: x + y, file_id_list)

    for file in file_id_list:

        cursor.execute('''SELECT tag_id, weight FROM tags WHERE fileid=? and source = "contents" ''', (file,))
        db.commit()
        tag_ids = cursor.fetchall()
        weight_list = []
        tag_id_list = []
        [weight_list.append(row[1]) for row in tag_ids]
        [tag_id_list.append(row[0]) for row in tag_ids]

        new_weights = lib.scale_values(weight_list)

        weight_id_iterable = dict(zip(tag_id_list, new_weights))

        for tag_id, nw in weight_id_iterable.items():
            cursor.execute('''UPDATE tags SET weight = ? where fileid = ? and tag_id =? ''', (nw, file, tag_id))
            db.commit()


def main():

    for file in file_list:

        fullpath = path + '/' + file
        contents = open(fullpath, 'r').read()

        corpus = lib.clean_text(contents)

        token_dict[file] = corpus

    # start the tf-idf method to generate weights
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')

    for file in file_list:

        # error handling loop to check for stop word values
        try:
            if token_dict[file] != '':
                # get tf values for each file
                tfs = tfidf.fit_transform([token_dict[file]])

                # get features (actual words)
                features = tfidf.get_feature_names()
                for word in tfs.nonzero()[1]:
                    if tfs[0, word] > 0.1:

                        tag = features[word]
                        print(tag)
                        # put data to db
                        lib.insert_tag(file, tag, 'contents', db, tfs[0, word])

            else:
                print('EMPTY=============')

        except ValueError:
            print("Stop words found!")

    normalize_tokens()


main()
