Purpose:
Service that uses natural language processing to find the most relevant documentation the user is searching for.

ideas for architecture:
user enters a search request for a topic such as REDACTED
The NLP parser needs to turn these into sql requests.
As we're not hoping for a real-time system just yet, a database is needed.
it will store all the word links, previous searches and all the key words from previous searches that will help it
find more relevant information each time you search. ( also for speed )
Thus firstly we wil look in the database to check if we can find any relevant info there, and serve that up in
relevance order. Then (second major module) scrape sharepoint (REDACTED and other file storage systems ) for any new
documents that are not in the index database.
The second module can also run on it's own to just add to the index database without user searches.

file list:
build_index.py  main function  finds the files in a location; for each file tokenizes the titles and cross refereces
with ons-specific terms to generate weighted tags

generate_weights.py  - called by build_index.py -  generates weights from the title tags , cross-referenced
against the word_jargon table which contains redacted-specific terms

pass2_contents.py - second step. reads the file contents and using tf-idf method adds weight to each work in the text(excluding stopwords)
then adds the most common terms to the database as tags

summaries.py - procedure to generate document summaries

populate_jargon.py preparation file to populate a lookup table

searchlib.py  library of common functions

create_db.py just a file to prepare and recreate the database

