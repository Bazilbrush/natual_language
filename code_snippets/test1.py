from nltk.book import *
fdist5 = FreqDist(text5)
character_words = sorted(w for w in set(text5) if len(w) > 7 and fdist5[w] > 7)
print(character_words)