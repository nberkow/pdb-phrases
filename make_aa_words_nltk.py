"""
parse a word list and remove words with characters that are not amio acid codes
"""

import sys
from nltk.corpus import words

allowed_characters = "ACDEFGHIKLMNPQRSTVWY"
whitelist = ['A', 'I']
blacklist = ['AL','AK','AZ','AR','CA',
             'CO','CT','DE','FL','GA',
             'HI','ID','IL','IN','IA',
             'KS','KY','LA',
             'MD',
             'MA','MI','MN','MS','MO',
             'MT','NE','NV','NH','NJ',
             'NM','NY','NC','ND','PA',
             'RI','SC','SD','TN','TX',
             'UT','VT','VA','WA','WV',
             'WI','WY']

for word in words.words():
    
    allowed = True
    uword = word.upper()

    i = 0

    while i < len(uword) and allowed:
        letter = uword[i]
        if letter not in allowed_characters:
            allowed = False
        i += 1

    if uword in blacklist:
        allowed = False

    if len(uword) < 2 and word not in whitelist:
        allowed = False
    
    if allowed:
        print(uword)

