"""
parse a word list and remove words with characters that are not amio acid codes
"""

import sys
from nltk.corpus import words

allowed_characters = "ACDEFGHIKLMNPQRSTVWY"

for word in words.words():
    
    allowed = True
    uword = word.upper()

    i = 0

    while i < len(uword) and allowed:
        letter = uword[i]
        if letter not in allowed_characters:
            allowed = False
        i += 1
    
    if allowed:
        print(uword)

