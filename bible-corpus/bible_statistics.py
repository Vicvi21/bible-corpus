# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import operator
import statistics
import math

from collections import OrderedDict


class IndBibleStatistics(object):
    
    def __init__(self):

        self.char_frequency = self.char_frequency()
        
        self.tok_frequency = self.token_frequency()
        self.tok_freq_by_length = self.calculate_token_frequencies_by_length()
        self.tokens_by_frequency = self.get_tokens_by_frequency()
        self.freqs_by_token_length = self.calculate_freq_by_tok_len()
        
        self.variance_by_tok_length = self.calculate_variance_by_token_length()
        self.variance_by_tok_freq = self.calculate_variance_by_token_freq()
        
        self.total_tokens = self.token_count()
        
        self.unique_chars = self.unique_chars()
        self.unique_tokens = self.unique_tokens()
        
        self.mean_char = statistics.mean(self.char_frequency.values())
        self.var_char = statistics.variance(self.char_frequency.values())
        self.std_char = math.sqrt(self.var_char)
        
        self.mean_tok = statistics.mean(self.tok_frequency.values())
        self.var_tok = statistics.variance(self.tok_frequency.values())
        self.std_tok = math.sqrt(self.var_tok)
        
        self.mean_fbtl = statistics.mean(self.freqs_by_token_length.values())
        self.var_fbtl = statistics.variance(
                                            self.freqs_by_token_length.values()
                                            )
        self.std_fbtl = math.sqrt(self.var_fbtl)
        
        self.z_scores_char = self.calculate_z_scores(self.char_frequency, 
                                                     self.mean_char, 
                                                     self.std_char)
        
        self.z_scores_tok = self.calculate_z_scores(self.tok_frequency, 
                                                    self.mean_tok, 
                                                    self.std_tok)
        
        self.z_scores_fbtl = self.calculate_z_scores(
                                                    self.freqs_by_token_length,
                                                    self.mean_fbtl, 
                                                    self.std_fbtl
                                                    )

    def calculate_freq_by_tok_len(self):
        res = {}
        for token, freq in self.tok_frequency.items():
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
    
    def cumulative_distribution_function(self, value):
        cumulative = 0
        for i in range(value + 1):
            freq_tok = self.freqs_by_token_length.get(i, 0)
            probability = freq_tok / self.total_tokens
            cumulative += probability
        return cumulative
    
    def calculate_token_frequencies_by_length(self):
        res = {}
        for token, frequency in self.tok_frequency.items():
            temp = res.get(len(token), {})
            temp[token] = frequency
            res[len(token)] = temp
        return res
    
    def get_tokens_by_frequency(self):
        res = {}
        for token, frequency in self.tok_frequency.items():
            temp = res.get(frequency, [])
            temp.append(token)
            res[frequency] = temp
        return res
    
    def calculate_variance_by_token_length(self):
        res = {}
        max_value = max(self.tok_freq_by_length)
        for i in range(max_value + 1):
            try:
                freqs = [value for _, value in \
                                            self.tok_freq_by_length[i].items()]
                res[i] = statistics.variance(freqs)
            except:
                res[i] = None
        return res
    
    def calculate_variance_by_token_freq(self):
        res = {}
        for freq, tokens in self.tokens_by_frequency.items():
            try:
                lengths = [len(value) for value in tokens]
                res[freq] = statistics.variance(lengths)
            except:
                res[freq] = None
        return res
            
    def as_dict(self):
        res = {}
        res["QtyOfTokens"] = self.total_tokens
        for key, value in self.freqs_by_token_length.items():
            res["StrLen_" + str(key)] = value
        for length, variance in self.variance_by_tok_length.items():
            res["VarFreq_StrLen_" + str(length)] = variance
        return res
    
    def plot(self):
        d = OrderedDict(sorted(self.freqs_by_token_length.items(), 
                               key=operator.itemgetter(0)))
        X = np.arange(len(d))
        plt.bar(X, d.values(), align='center', width=0.5)
        plt.xticks(X, d.keys())
        ymax = max(d.values()) + 3000
        plt.ylim(0, ymax)
        plt.ylabel("Cantidad de palabras")
        plt.xlabel("Cantidad de caracteres en la palabra")
        plt.title(self.language)
        plt.show()
    

class BibleGroup(object):
    
    def __init__(self):
        self.bibles = []
    
    @property
    def column_headers(self):
        basic_headers = ["QtyOfTokens"]
        length_set = set()
        for bible in self.bibles:
            for key in bible.freqs_by_token_length.keys():
                length_set.add(key)
        length_headers = ["StrLen_" + str(length) for length in \
                                                     sorted(length_set)]
        
        var_headers = ["VarFreq_StrLen_" + str(length) for length in \
                                                     sorted(length_set)]
        return basic_headers + length_headers + var_headers
    
    def plot_cumulative_dist(self):
        
        for bible in self.bibles:
            values = []
            x = []
            for i in range(36):
                values.append(bible.cumulative_distribution_function(i))
                x.append(i)
            plt.plot(x, values)
        plt.xticks(x)
        plt.show()
    
    def add(self, bible):
        if not isinstance(bible, IndBibleStatistics):
            raise TypeError("Not correct IndBibleStatistics type")
        self.bibles.append(bible)
        
    def to_dataframe(self, *set_of_bibles):
        dataframe = pd.DataFrame(columns=self.column_headers)
        for bible in self.bibles:
            dataframe.loc[bible.language] = pd.Series(bible.as_dict())
        return dataframe