# -*- coding:utf-8 -*-


import os
import sys
from bible import Bible
from bible_statistics import BibleGroup
from generate import RandomBible


source_dirs = ["../bibles/Usable/",
               "../bibles/Random/",
               "../bibles/Random_Space_Char/",
               "../bibles/Testing/"]

parent_dirs = ["Usable/",
               "Random/",
               "Random_Space_Char/"]

# Configuration
selected_dir = 0
generate_random = True
generate_whitespace_random = True
make_plots = False
process = False

bibles = BibleGroup()

for _, _, filenames in os.walk(source_dirs[selected_dir]):
    for filename in filenames:
        new_bible = Bible.from_path(source_dirs[selected_dir] + filename)
        if len(new_bible) > 27:
            new_bible = new_bible.get_new_testament()
        bibles.add(new_bible)
        print("({0}) Counted toks: {1}, Reported: {2}".format(
                                                new_bible.language,
                                                new_bible.token_count(),
                                                new_bible.reported_word_count
                                                )
              )
        if make_plots:
            plot_folder = "../plots/" + parent_dirs[selected_dir]
            new_bible.plot_freq_long(plot_folder=plot_folder)
            new_bible.plot_freq_varlong(plot_folder=plot_folder)
            new_bible.plot_long_freq(plot_folder=plot_folder)
            new_bible.plot_long_varfreq(plot_folder=plot_folder)
            new_bible.plot_freq_meanlong(plot_folder=plot_folder)
        
        if generate_random:
            random_bible = RandomBible.create_xml_from(new_bible,
                                                       source_dirs[1],
                                                       False)
            
        if generate_whitespace_random:
            random_whitespace_bibles = RandomBible.create_xml_from(
                                                                new_bible,
                                                                source_dirs[2],
                                                                True)
        
if process:
    dataframe = bibles.to_dataframe()
    dataframe = dataframe.dropna(axis=1,how='all')
    
    dataframe.to_csv("../results/" + parent_dirs[selected_dir] + \
                                                "bible_word_frequency_data.csv")
    summary = dataframe.describe()
    summary.to_csv("../results/" + parent_dirs[selected_dir] + \
                                        "summary_bible_word_frequency_data.csv")
    
    corrs = dataframe.corr("spearman")
    corrs = corrs.dropna(axis=0, how="all")
    corrs = corrs.dropna(axis=1, how="all")
    #corrs.to_csv("../results/correlation_matrix.csv")
    
    spearman = bibles.spearman_dataframe()
    spearman.to_csv("../results/" + parent_dirs[selected_dir] + \
                                                            "spearman_cors.csv")
    
    #spearman_var = bibles.spearman_var_dataframe()
    #spearman_var.to_csv("../results/spearman_var_cors.csv")
    
    #spearman_novar = bibles.spearman_novar_dataframe()
    #spearman_novar.to_csv("../results/spearman_novar_cors.csv")
    
    #bibles.plot_cumulative_dist()
    #import ipdb;ipdb.set_trace()