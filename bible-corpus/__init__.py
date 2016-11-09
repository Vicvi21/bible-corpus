# -*- coding:utf-8 -*-


import os
from bible import Bible
from bible_statistics import BibleStatistics
import bible as bib


source_dir = "../bibles/Usable/"

bibles = []

i = 0
for _, _, filenames in os.walk(source_dir):
    for filename in filenames:
        new_bible = Bible.from_path(source_dir + filename)
        if len(new_bible) > 27:
            new_bible = new_bible.get_new_testament()
        bibles.append(new_bible)
        print("({0}) Counted toks: {1}, Reported: {2}".format(
                                                new_bible.language,
                                                new_bible.token_count(),
                                                new_bible.reported_word_count
                                                )
              )
        i += 1
        if i == 1:
            break
import ipdb;ipdb.set_trace()