# mock up of summarising

# load up a text file

# split into sentences

# load up the corresponding tags from database

# find sentences that have the largest amount of tags

# maybe include bigram analysis?

# write the best candidates to database - no need yet


import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer, sent_tokenize
import searchlib as lib
from untokenize import untokenize

path = 'C:/Users/bazilj/PycharmProjects/nltk_test/text_samples/CS Results Retrieving archived data.txt'

contents = open(path, 'r').read()

clean = lib.clean_text(contents)
tokens = lib.tokenize(clean)


lemma = WordNetLemmatizer()

token_dict = dict([])
lemmed = []
for token in tokens:
    # create a dictionary of transformations
    token_dict[token] = lemma.lemmatize(token, lib.get_wordnet_pos(nltk.pos_tag(nltk.word_tokenize(token))[0][1]))
    # root words separated
    lemmed.append(lemma.lemmatize(token, lib.get_wordnet_pos(nltk.pos_tag(nltk.word_tokenize(token))[0][1])))


# calculate frequency dist. This is where we can improve the quality of summarisation by using a different algorithm


fdist1 = nltk.FreqDist(lemmed)
# get the whole scoring set - there's probably a better method
scoring_set = dict(fdist1.most_common(len(fdist1)))

# split into sentences


tokenizer_words = TweetTokenizer()
tokens_sentences = [tokenizer_words.tokenize(t) for t in nltk.sent_tokenize(contents)]


# score sentences based on the frequency distribution of the words
for sentence in tokens_sentences:

    sentence_roots = [lemma.lemmatize(sentence_word, lib.get_wordnet_pos(nltk.pos_tag(nltk.word_tokenize(sentence_word))[0][1])) for sentence_word in sentence]

    # to score the words in the sentence
    # we gonna:
    # put original and lemmed as a dictionary where {orig_word = lemmed_word}
    sentence_dict = dict(zip(sentence, sentence_roots))
    # compare the lemmed words in the dictionary to the fdist most common,
    for term, term_lemma in sentence_dict.items():

        for key, val in scoring_set.items():
            if term_lemma == key:
                sentence_dict[term] = val
    # when match found sub the lemmed word for the word score.

    # sum the scores
    total_score = 0
    for word, score in sentence_dict.items():

        if word.isnumeric():
            pass
        else:
            if isinstance(score, int):
                total_score += score

    # add score to the start of the sentence
    sentence.insert(0, total_score)


# find highest ranked sentences and return in the correct order
final_list = dict([])
for i in range(0, 6):
    max1 = [0, 0]
    for j in range(len(tokens_sentences)):

        if tokens_sentences[j][0] > max1[1]:

            max1[1] = tokens_sentences[j][0]
            # store the index
            max1[0] = j

    # insert at index - we preserve the position by storing the index as the key
    final_list[max1[0]] = tokens_sentences[max1[0]]
    # remove at index
    tokens_sentences.pop(max1[0])

print(sorted(final_list))


# detokenize - and order


for i in range(0, len(sorted(final_list))):
    print(sorted(final_list)[i])

    statement = final_list[sorted(final_list)[i]]
    # remove the score
    statement.pop(0)
    condensed = untokenize(statement)

    print(condensed)

