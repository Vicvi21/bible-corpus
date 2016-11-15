# -*- coding:utf-8 -*-


import os
from bible import Bible
from bible_statistics import BibleGroup


source_dir = "../bibles/Usable/"

bibles = BibleGroup()
i = 0
for _, _, filenames in os.walk(source_dir):
    for filename in filenames:
        new_bible = Bible.from_path(source_dir + filename)
        if len(new_bible) > 27:
            new_bible = new_bible.get_new_testament()
        bibles.add(new_bible)
        print("({0}) Counted toks: {1}, Reported: {2}".format(
                                                new_bible.language,
                                                new_bible.token_count(),
                                                new_bible.reported_word_count
                                                )
              )
        i += 1
        #if i == 4:
        #    break

dataframe = bibles.to_dataframe()
dataframe = dataframe.dropna(axis=1,how='all')

dataframe.to_csv("../bible_word_frequence_data.csv")
summary = dataframe.describe()
summary.to_csv("../summary_bible_word_frequence_data.csv")

corrs = dataframe.corr("spearman")
corrs = corrs.dropna(axis=0, how="all")
corrs = corrs.dropna(axis=1, how="all")
corrs.to_csv("../correlation_matrix.csv")

spearman = bibles.spearman_dataframe()
spearman.to_csv("../spearman_cors.csv")
#bibles.plot_cumulative_dist()
import ipdb;ipdb.set_trace()