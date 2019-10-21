from nltk.book import *
print(sent7)

# print all words less than 4 chars long
print([w for w in sent7 if len(w) < 4])

# print all words less less or eq to 4 chars long
print([w for w in sent7 if len(w) <= 4])

# print all words 4 chrs long
print([w for w in sent7 if len(w) == 4])

# print all that are not 4 chars long
print([w for w in sent7 if len(w) != 4])

# ends with
print(sorted(w for w in set(text1) if w.endswith('ableness')))

