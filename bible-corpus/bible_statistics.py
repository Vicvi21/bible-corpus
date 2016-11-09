# -*- coding:utf-8 -*-

import pandas as pd
import operator
import statistics
import math
from collections import OrderedDict


class BibleStatistics(object):
    
    def __init__(self, bible):
        self.language = bible.language
        self.char_frequency = bible.char_frequency()
        self.token_frequency = bible.token_frequency()
        self.total_tokens = bible.token_count()
        self.unique_chars = bible.unique_chars()
        self.unique_tokens = bible.unique_tokens()
        
    @property
    def freq_by_token_length(self):
        res = {}
        for token, freq in self.token_frequency.items():
            res[len(token)] = res.get(len(token), 0) + freq
        return OrderedDict(sorted(res.items(), 
                                  key=operator.itemgetter(1), 
                                  reverse=True)
                           )
    
    @property
    def mean(self):
        res = statistics.mean(self.normalize(self.freq_by_token_length
                                             ).values())
        return res
    
    @property
    def distance_from_mean(self):
        res = OrderedDict({})
        for key, value in self.normalize(self.freq_by_token_length).items():
            res[key] = abs(value - self.mean)
        return res
    
    def normalize(self, dic_to_norm):
        max_value = max(dic_to_norm.values())
        res = OrderedDict({})
        for key, value in dic_to_norm.items():
            res[key] = value / max_value
        return res