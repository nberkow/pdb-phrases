import os
import re

topdir = "data/Albums"
allowed_characters = set("ACDEFGHIKLMNPQRSTVWY")
subdirs = os.listdir(topdir)

with open("lyric_meta.txt", 'w') as meta, open("bracelets.txt", "w") as bracelets:

    done = set()
    for album in subdirs:
        files = os.listdir(topdir + "/" + album)
        for f in files:
            froot = re.split('_|\.', f)[0].upper()

            if set(froot) <= allowed_characters:
                print(f"{froot}", file=bracelets)   
            with open(topdir + "/" + album + "/" + f, 'r') as lyrics_file:
                for lyr in lyrics_file:
                    substrings = re.split(',|\.', lyr)
                    for substr in substrings:

                        acronym = ""
                        words = substr.rstrip().split(" ")
                        clean = True

                        for w in words:
                            if len(w) > 0:
                                w = re.sub(r'\W+', '', w)
                                w = re.sub(r"'",   '', w)
                                w = re.sub(r'"',   '', w)
                                w = re.sub(r"[\([{})\]]",   '', w)
                                w = w.upper()
                                if len(w) > 0:
                                    acronym += w[0]

                        if len(acronym) > 5 and set(acronym) <= allowed_characters and acronym not in done:
                            done.add(acronym)
                            print(f"{album}\t{f}\t{acronym}\t{substr.rstrip()}", file=meta)
                            print(f"{acronym}", file=bracelets)    
