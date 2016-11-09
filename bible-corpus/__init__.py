# -*- coding:utf-8 -*-


import os
from bible import Bible
import bible as bib


source_dir = "../bibles/Usable/"

bibles = []

i = 0
for _, _, filenames in os.walk(source_dir):
    for filename in filenames:
        new_bible = Bible(source_dir + filename)
        bibles.append(new_bible)
        print("({0}) Counted toks: {1}, Reported: {2}".format(
                                                new_bible.language,
                                                new_bible.token_count(),
                                                new_bible.reported_word_count
                                                )
              )
single = bibles[0]        
import ipdb;ipdb.set_trace()