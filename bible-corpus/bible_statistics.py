# -*- coding:utf-8 -*-

import pandas as pd
import operator
import statistics
import math
from collections import OrderedDict


class BibleStatistics(object):
    
    def __init__(self, bible):
        self.bible = bible
        self.language = bible.language
        
        self.char_frequency = bible.char_frequency()
        self.token_frequency = bible.token_frequency()
        self.freqs_by_token_length = self.calculate_freq_by_tok_len()
        
        self.total_tokens = bible.token_count()
        
        self.unique_chars = bible.unique_chars()
        self.unique_tokens = bible.unique_tokens()
        
        self.mean_char = statistics.mean(self.char_frequency.values())
        self.var_char = statistics.variance(self.char_frequency.values())
        self.std_char = math.sqrt(self.var_char)
        
        self.mean_tok = statistics.mean(self.token_frequency.values())
        self.var_tok = statistics.variance(self.token_frequency.values())
        self.std_tok = math.sqrt(self.var_tok)
        
        self.mean_fbtl = statistics.mean(self.freqs_by_token_length.values())
        self.var_fbtl = statistics.variance(
                                            self.freqs_by_token_length.values()
                                            )
        self.std_fbtl = math.sqrt(self.var_fbtl)
        
        self.z_scores_char = self.calculate_z_scores(self.char_frequency, 
                                                     self.mean_char, 
                                                     self.std_char)
        
        self.z_scores_tok = self.calculate_z_scores(self.token_frequency, 
                                                    self.mean_tok, 
                                                    self.std_tok)
        
        self.z_scores_fbtl = self.calculate_z_scores(
                                                    self.freqs_by_token_length,
                                                    self.mean_fbtl, 
                                                    self.std_fbtl
                                                    )

    def calculate_freq_by_tok_len(self):
        res = {}
        for token, freq in self.token_frequency.items():
            res[len(token)] = res.get(len(token), 0) + freq
        return OrderedDict(sorted(res.items(), 
                                  key=operator.itemgetter(1), 
                                  reverse=True)
                           )
    
    def calculate_z_scores(self, data_dict, mean, std):
        res = data_dict.copy()
        for key, value in res.items():
            res[key] = (value - mean) / std
        return res