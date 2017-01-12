# -*- coding:utf-8 -*-


import os
import sys
from bible import Bible
from bible_statistics import BibleGroup
from generate import RandomBible

source_dirs = ["../bibles/Usable/",
               "../bibles/Random/",
               "../bibles/Random_Space_Char/"]

generate_random = False
generate_whitespace_random = False

if len(sys.argv) < 2:
    sys.exit("Usage: %s Number_source_folder [generate [1|2|3]]" % sys.argv[0])
if len(sys.argv) >= 2:
    number_folder_source = int(sys.argv[1])
    if number_folder_source >= len(source_dirs):
        print("Folder source is between 0 and %d" % len(source_dirs)-1)
        sys.exit("Usage: %s Number_source_folder [generate [1|2|3]]" % sys.argv[0])
if len(sys.argv) == 3:
    if sys.argv[1] == "generate":
        if sys.argv[2] == "1":
            # Only Random
            generate_random = True
        elif sys.argv[2] == "2":
            # Random white characters
            generate_whitespace_random = True
        elif sys.arg[2] == "3":
            # Both 
            generate_random = True
            generate_whitespace_random = True

bibles = BibleGroup()
random_bibles = BibleGroup()
random_whitespace_bibles = BibleGroup()

i = 0
for _, _, filenames in os.walk(source_dirs[0]):
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
        new_bible.plot_freq_long()
        new_bible.plot_freq_varlong()
        new_bible.plot_long_freq()
        new_bible.plot_long_varfreq()
        new_bible.plot_freq_meanlong()
        
        if generate_random:
            random_bible = RandomBible.create_xml_from(new_bible,
                                           source_dirs[1],
                                           False)
            
        if generate_whitespace_random:
            random_bible = RandomBible.create_xml_from(new_bible,
                                           source_dirs[2],
                                           True)
        

dataframe = bibles.to_dataframe()
dataframe = dataframe.dropna(axis=1,how='all')

dataframe.to_csv("../results/bible_word_frequency_data.csv")
summary = dataframe.describe()
summary.to_csv("../results/summary_bible_word_frequency_data.csv")

corrs = dataframe.corr("spearman")
corrs = corrs.dropna(axis=0, how="all")
corrs = corrs.dropna(axis=1, how="all")
#corrs.to_csv("../results/correlation_matrix.csv")

spearman = bibles.spearman_dataframe()
spearman.to_csv("../results/spearman_cors.csv")

#spearman_var = bibles.spearman_var_dataframe()
#spearman_var.to_csv("../results/spearman_var_cors.csv")

#spearman_novar = bibles.spearman_novar_dataframe()
#spearman_novar.to_csv("../results/spearman_novar_cors.csv")

#bibles.plot_cumulative_dist()
#import ipdb;ipdb.set_trace()