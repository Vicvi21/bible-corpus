# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats
import gc

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
        
        # Token Length frequencies
        for length, qty_of_tkns in self.freqs_by_token_length.items():
            res["QtyTokens_StrLen_" + str(length)] = qty_of_tkns
            
         # No. of Tokens by frequencies
        for freq, lst_tok in self.tokens_by_frequency.items():
            res["QtyTokens_Freq_" + str(freq)] = len(lst_tok)
        
        # Token frequencies variance by length
        for length, freq_variance in self.variance_by_tok_length.items():
            res["VarFreq_StrLen_" + str(length)] = freq_variance
        
        # Token length variance by frequency
        for freq, len_variance in self.variance_by_tok_freq.items():
            res["VarStrLen_Freq_" + str(freq)] = len_variance
            
        return res
    
    def plot_freq_long(self, annotated=False, save=True, folder="../plots/freq_long/"):
        dataset = [(token, frequency, len(token)) for token, frequency in \
                                                    self.tok_frequency.items()]
        label_set = {}
        for label, x, y in dataset:
            x_coord = label_set.get(x, {})
            xy_coord = x_coord.get(y, set([]))
            xy_coord.add(label)
            
            x_coord[y] = xy_coord
            label_set[x] = x_coord
            
        if save:
            #plt.figure(figsize=(33.1, 46.8))
            #plt.plot()
            #plt.figure(figsize=(46.8, 33.1), dpi=300)
            fig = plt.figure(figsize=(11.69, 8.27))
        
        plt.yticks(range(max(self.tok_freq_by_length) + 1))
        #res = np.logspace(np.log10(0.01), np.log10(max(self.tokens_by_frequency)))
        res = [n for n in range(0, 
                                max(self.tokens_by_frequency), 
                                int(max(self.tokens_by_frequency)/15)
                                )
               ]
        plt.xticks(res)
        
        # X frequency Y length 
        ndataset = np.array(dataset)
        plt.scatter(np.array(ndataset[:, 1], dtype=np.int32), 
                    np.array(ndataset[:, 2], dtype=np.int32),
                    marker = 'o',)
        
        if annotated:
            for label, x, y in dataset:
                try:
                    plt.annotate(str(label_set[x][y]),
                                 xy=(x, y))
                    del label_set[x][y]
                except:
                    pass
                
        plt.ylabel("Token Length")
        plt.xlabel("Token Frequency")
        plt.title(self.language)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        if save:
            plt.savefig(folder + self.language)
            fig.clf()
        else:
            plt.show()
        plt.close()
        gc.collect()
            
    def plot_freq_varlong(self, save=True, folder="../plots/freq_varlong/"):
        dataset = [(frequency, l_variance) for frequency, l_variance in \
                                            self.variance_by_tok_freq.items()
                                            if l_variance != None]
        
        if save:
            fig = plt.figure(figsize=(11.69, 8.27))
        
        # X frequency Y length 
        ndataset = np.array(dataset)
        plt.bar(np.array(ndataset[:, 0], dtype=np.int32), 
                np.array(ndataset[:, 1], dtype=np.int32))
        
        plt.ylabel("Variance of Token Lengths by Frequency")
        plt.xlabel("Token Frequency")
        plt.title(self.language)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        if save:
            plt.savefig(folder + self.language)
            fig.clf()
        else:
            plt.show()
        plt.close()
        gc.collect()

    def plot_long_freq(self, annotated=False, save=True, folder="../plots/long_freq/"):
        dataset = [(token, frequency, len(token)) for token, frequency in \
                                                    self.tok_frequency.items()]
        label_set = {}
        for label, x, y in dataset:
            x_coord = label_set.get(x, {})
            xy_coord = x_coord.get(y, set([]))
            xy_coord.add(label)
            
            x_coord[y] = xy_coord
            label_set[x] = x_coord
            
        if save:
            #plt.figure(figsize=(33.1, 46.8))
            #plt.plot()
            #plt.figure(figsize=(46.8, 33.1), dpi=300)
            fig = plt.figure(figsize=(11.69, 8.27))
        
        plt.xticks(range(max(self.tok_freq_by_length) + 1))
        #res = np.logspace(np.log10(0.01), np.log10(max(self.tokens_by_frequency)))
        res = [n for n in range(0, 
                                max(self.tokens_by_frequency), 
                                int(max(self.tokens_by_frequency)/15)
                                )
               ]
        plt.yticks(res)
        
        # Y frequency X length 
        ndataset = np.array(dataset)
        plt.scatter(np.array(ndataset[:, 2], dtype=np.int32), 
                    np.array(ndataset[:, 1], dtype=np.int32),
                    marker = 'o',)
        
        if annotated:
            for label, y, x in dataset:
                try:
                    plt.annotate(str(label_set[x][y]),
                                 xy=(x, y))
                    del label_set[x][y]
                except:
                    pass
                
        plt.xlabel("Token Length")
        plt.ylabel("Token Frequency")
        plt.title(self.language)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        if save:
            plt.savefig(folder + self.language)
            fig.clf()
        else:
            plt.show()
        plt.close()
        gc.collect()
        
    def plot_long_varfreq(self, save=True, folder="../plots/long_varfreq/"):
        dataset = [(token_length, f_variance) for token_length, f_variance in \
                                        self.variance_by_tok_length.items()\
                                        if f_variance != None]
            
        if save:
            fig = plt.figure(figsize=(11.69, 8.27))
        
        plt.xticks(range(max(self.variance_by_tok_length) + 1))
        # Y varfrequency X length 
        ndataset = np.array(dataset)
        plt.bar(np.array(ndataset[:, 0], dtype=np.int32), 
                np.array(ndataset[:, 1], dtype=np.int32))
        
        plt.xlabel("Token Length")
        plt.ylabel("Variance of Token Frequency by Length")
        plt.title(self.language)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        if save:
            plt.savefig(folder + self.language)
            fig.clf()
        else:
            plt.show()
        plt.close()
        gc.collect()
    
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
        
        self.basic_headers = ["QtyOfTokens"]
        self.length_set = set()
        self.freq_set = set()
        
    
    def calculate_freq_length_sets(self):
        for bible in self.bibles:
            for length in bible.freqs_by_token_length.keys():
                self.length_set.add(length)
            for freq in bible.tokens_by_frequency.keys():
                self.freq_set.add(freq)
        return self.length_set, self.freq_set
    
    @property
    def length_headers(self):
        length_headers = ["QtyTokens_StrLen_" + str(length) for length in \
                                                     sorted(self.length_set)]
        return length_headers
    
    @property
    def freq_headers(self):
        freq_headers = ["QtyTokens_Freq_" + str(freq) for freq in \
                                                     sorted(self.freq_set)]
        return freq_headers
    
    @property
    def varfreq_headers(self):
        varfreq_headers = ["VarFreq_StrLen_" + str(length) for length in \
                                                     sorted(self.length_set)]
        return varfreq_headers
    
    @property
    def varstrlen_headers(self):
        varstrlen_headers = ["VarStrLen_Freq_" + str(freq) for freq in \
                                                     sorted(self.freq_set)]
        return varstrlen_headers
    
    @property
    def column_headers(self):
        self.calculate_freq_length_sets()
        return self.basic_headers + \
               self.length_headers + \
               self.freq_headers + \
               self.varfreq_headers + \
               self.varstrlen_headers
    
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
        
    def spearman_dataframe(self):
        df = self.to_dataframe()
        
        res = pd.DataFrame(columns=["VarFreq_times_StrLen", 
                                    "Rho_VarFreq_times_StrLen", 
                                    "Pi_VarFreq_times_StrLen",
                                    "VarStrLen_times_Freq", 
                                    "Rho_VarStrLen_times_Freq", 
                                    "Pi_VarStrLen_times_Freq",
                                    ])
        
        # tokens by length_vector
        freq_by_len = self.length_headers
        freq_by_len_df = df[freq_by_len]
        
        # variance of freq by len
        var_freq_by_len = self.varfreq_headers
        var_freq_by_len_df = df[var_freq_by_len]
        
        # tokens by freq vector
        len_by_freq = self.freq_headers
        len_by_freq_df = df[len_by_freq]
        
        # variance of len by freq
        var_len_by_freq = self.varstrlen_headers
        var_len_by_freq_df = df[var_len_by_freq]

        for i in range(len(freq_by_len_df)):
            row_res = {}
 
            language = freq_by_len_df.iloc[i].name
            
            vect1 = freq_by_len_df.iloc[i].as_matrix()
            vect2 = var_freq_by_len_df.iloc[i].as_matrix()
            
            rho, pi = self.spearmanr(vect1, vect2)
            row_res["VarFreq_times_StrLen"] = np.sum(
                                                np.nan_to_num(vect1 * vect2)
                                                )
            row_res["Rho_VarFreq_times_StrLen"] = rho
            row_res["Pi_VarFreq_times_StrLen"] = pi
            
            vect1 = len_by_freq_df.iloc[i].as_matrix()
            vect2 = var_len_by_freq_df.iloc[i].as_matrix()
            
            rho, pi = self.spearmanr(vect1, vect2)
            row_res["VarStrLen_times_Freq"] = np.sum(
                                                np.nan_to_num(vect1 * vect2)
                                                )
            row_res["Rho_VarStrLen_times_Freq"] = rho
                    
            row_res["Pi_VarStrLen_times_Freq"] = pi
            
            res.loc[language] = pd.Series(row_res) 
        
        return res

    def spearmanr(self, array1, array2):
        x1 = np.ma.masked_invalid(array1)
        y1 = np.ma.masked_invalid(array2)
        m = np.ma.mask_or(np.ma.getmask(x1), np.ma.getmask(y1))
        k = np.ma.array(x1, mask=m, copy=True).compressed()
        j = np.ma.array(y1, mask=m, copy=True).compressed()
        return scipy.stats.spearmanr(k, j, nan_policy='omit')
        
    def to_dataframe(self):
        dataframe = pd.DataFrame(columns=self.column_headers)
        for bible in self.bibles:
            dataframe.loc[bible.language] = pd.Series(bible.as_dict())
        return dataframe