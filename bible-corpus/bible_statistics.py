# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as ss
import Bio.Cluster as bc
from rpy2.robjects.packages import importr
import gc

import operator
import statistics
import math

from collections import OrderedDict

psych = importr("psych")


class IndBibleStatistics(object):
    
    def __init__(self, lower_case=True):

        self.char_frequency = self.char_frequency(lower_case)
        
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
    
    def plot_freq_long(self, annotated=False, save=True, 
                       plot_folder="../plots/", 
                       sub_folder="freq_long/"):
        folder = plot_folder + sub_folder
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
        x_distance = min(max(self.tokens_by_frequency), 15)
        res = [n for n in range(0, 
                                max(self.tokens_by_frequency), 
                                int(max(self.tokens_by_frequency)/x_distance)
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
    
    def plot_freq_meanlong(self, annotated=False, save=True,
                           plot_folder="../plots/", 
                           sub_folder="freq_meanlong/"):
        folder = plot_folder + sub_folder
        dataset = []
        for freq, tokens in self.tokens_by_frequency.items():
            len_values = []
            for token in tokens:
                len_values.append(len(token))
            mean_val = statistics.mean(len_values)
            dataset.append((freq, mean_val))
            
        if save:
            fig = plt.figure(figsize=(11.69, 8.27))
        
        # X frequency Y mean length 
        ndataset = np.array(sorted(dataset))
        plt.bar(np.array(ndataset[:, 0], dtype=np.int32), 
                np.array(ndataset[:, 1], dtype=np.int32))
        
        plt.ylabel("Mean of Token Lengths")
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
            
    def plot_freq_varlong(self, save=True, 
                          plot_folder="../plots/", 
                          sub_folder="freq_varlong/"):
        folder = plot_folder + sub_folder
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

    def plot_long_freq(self, annotated=False, save=True, 
                       plot_folder="../plots/", 
                       sub_folder="long_freq/"):
        folder = plot_folder + sub_folder
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
        y_distance = min(max(self.tokens_by_frequency), 15)
        res = [n for n in range(0, 
                                max(self.tokens_by_frequency), 
                                int(max(self.tokens_by_frequency)/y_distance)
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
        
    def plot_long_varfreq(self, save=True, 
                          plot_folder="../plots/", 
                          sub_folder="long_varfreq/"):
        folder = plot_folder + sub_folder

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
        # Efectivament |Rho_Freq_StrLen| < |Rho_Freq_MeanStrLen| < |Rho_Freq_VarStrLen|, 
        # tal com esperava. Sembla que tenim una nova llei que és més forta que la
        # llei de brevetat original. Per poder comparar correlacions de forma 
        # estadísticament rigorosa caldria usar un test de 
        # Hotteling / Steiger’s (o semblant per a correlació de Spearman), 
        # perquè en la comparativa que tenim més amunt, 
        # Rho_Freq_MeanStrLen i Rho_Freq_VarStrLen compateixen la mateixa 
        # de columna de freqüències de la matriu. Aquests testos tenen l'objectiu 
        # de determinar si la diferència entre dues correlacions és realment 
        # significativa. Poso la mà al foc a què ho és perquè de forma sistemàtica 
        # en diferents llengües tenim |Rho_Freq_MeanStrLen| < |Rho_Freq_VarStrLen|
        
        df = self.to_dataframe()
        
        res = pd.DataFrame(columns=["Rho_Freq_StrLen", 
                                    "P_Freq_StrLen",
                                    
                                    "Rho_StrLen_VarFreq_NOVAR0", 
                                    "P_StrLen_VarFreq_NOVAR0",
                                    "Rho_Freq_VarStrLen_NOVAR0",
                                    "P_Freq_VarStrLen_NOVAR0",
                                    "Rho_Freq_MeanStrLen_NOVAR0",
                                    "P_Freq_MeanStrLen_NOVAR0",
                                    "Rho_VarStrLen_MeanStrLen_NOVAR0",
                                    "P_VarStrLen_MeanStrLen_NOVAR0",
                                    
                                    "Steiger_t_Freq_VarStrLen_MeanStrLen_NOVAR0",
                                    "Steiger_p_Freq_VarStrLen_MeanStrLen_NOVAR0",
                                    
                                    "Rho_StrLen_VarFreq_VAR0", 
                                    "P_StrLen_VarFreq_VAR0",
                                    "Rho_Freq_VarStrLen_VAR0",
                                    "P_Freq_VarStrLen_VAR0",
                                    "Rho_Freq_MeanStrLen_VAR0",
                                    "P_Freq_MeanStrLen_VAR0",
                                    "Rho_VarStrLen_MeanStrLen_VAR0",
                                    "P_VarStrLen_MeanStrLen_VAR0",
                                    
                                    "Steiger_t_Freq_VarStrLen_MeanStrLen_VAR0",
                                    "Steiger_p_Freq_VarStrLen_MeanStrLen_VAR0"
                                    ])
        
        for bible in self.bibles:
            row_res = {}
            
            # X frequencies Y lengths 
            dataset = []
            for freq, tokens in bible.tokens_by_frequency.items():
                for token in tokens:
                    dataset.append((freq, len(token)))
        
            freq_len_dset = np.array(sorted(dataset))
            sper_freq_len_dset = self.spearmanr(freq_len_dset[:, 0], 
                                                freq_len_dset[:, 1], 
                                                True)
            
            row_res["Rho_Freq_StrLen"] = sper_freq_len_dset[0]
            row_res["P_Freq_StrLen"] = sper_freq_len_dset[1]

            # X length Y frequency variance is None
            dataset = [(token_length, f_variance) for token_length, f_variance in \
                                        bible.variance_by_tok_length.items()\
                                        if f_variance != None]
            
            len_fvar_dset = np.array(sorted(dataset))
            sper_len_fvar_dset = self.spearmanr(len_fvar_dset[:, 0], 
                                                len_fvar_dset[:, 1], 
                                                True)
            
            row_res["Rho_StrLen_VarFreq_NOVAR0"] = sper_len_fvar_dset[0]
            row_res["P_StrLen_VarFreq_NOVAR0"] = sper_len_fvar_dset[1]

            
            # X frequency Y length_variance when varstrlen is None
            dataset = [(frequency, l_variance) for frequency, l_variance in \
                                            bible.variance_by_tok_freq.items()
                                            if l_variance != None]
            
            freq_lvar_dset = np.array(sorted(dataset))
            sper_freq_lvar_dset = self.spearmanr(freq_lvar_dset[:, 0], 
                                                 freq_lvar_dset[:, 1], 
                                                 True)
            
            row_res["Rho_Freq_VarStrLen_NOVAR0"] = sper_freq_lvar_dset[0]
            row_res["P_Freq_VarStrLen_NOVAR0"] = sper_freq_lvar_dset[1]
            
            # X frequencies Y Mean Lengths when varstrlen is None
            dataset = []
            for freq, tokens in bible.tokens_by_frequency.items():
                if bible.variance_by_tok_freq[freq] != None: # Variance is None
                    len_values = []
                    for token in tokens:
                        len_values.append(len(token))
                    mean_val = statistics.mean(len_values)
                    dataset.append((freq, mean_val))
            
            freq_mlen_dset = np.array(sorted(dataset))
            sper_freq_mlen_dset = self.spearmanr(freq_mlen_dset[:, 0], 
                                                freq_mlen_dset[:, 1], 
                                                True)
            
            row_res["Rho_Freq_MeanStrLen_NOVAR0"] = sper_freq_mlen_dset[0]
            row_res["P_Freq_MeanStrLen_NOVAR0"] = sper_freq_mlen_dset[1]
            
            # X length_variance Y mean lengths when varstrlen is None
            lvar_mlen_dset = np.column_stack((freq_lvar_dset[:, 1],
                                              freq_mlen_dset[:, 1]))
            sper_lvar_mlen_dset = self.spearmanr(lvar_mlen_dset[:, 0],
                                                 lvar_mlen_dset[:, 1],
                                                 True)
            row_res["Rho_VarStrLen_MeanStrLen_NOVAR0"] = sper_lvar_mlen_dset[0]
            row_res["P_VarStrLen_MeanStrLen_NOVAR0"] = sper_lvar_mlen_dset[1]
            
            # Steiger's Z
            steiger = psych.r_test(n=len(lvar_mlen_dset), 
                                   r12=row_res["Rho_Freq_VarStrLen_NOVAR0"], 
                                   r13=row_res["Rho_Freq_MeanStrLen_NOVAR0"], 
                                   r23=row_res["Rho_VarStrLen_MeanStrLen_NOVAR0"]
                                   )
            row_res["Steiger_t_Freq_VarStrLen_MeanStrLen_NOVAR0"] = steiger[2][0]
            row_res["Steiger_p_Freq_VarStrLen_MeanStrLen_NOVAR0"] = steiger[3][0]

            
            ########
            
            # X length Y frequency variance as zero
            dataset = [(token_length, f_variance) for token_length, f_variance in \
                                        bible.variance_by_tok_length.items()]
            
            len_fvar_dset = np.nan_to_num(np.array(sorted(dataset),
                                                   dtype=np.float)
                                           )
            sper_len_fvar_dset = self.spearmanr(len_fvar_dset[:, 0], 
                                                len_fvar_dset[:, 1], 
                                                True)
            
            row_res["Rho_StrLen_VarFreq_VAR0"] = sper_len_fvar_dset[0]
            row_res["P_StrLen_VarFreq_VAR0"] = sper_len_fvar_dset[1]
            
            # X frequency Y length_variance varstrl as zero
            dataset = [(frequency, l_variance) for frequency, l_variance in \
                                            bible.variance_by_tok_freq.items()]
            
            freq_lvar_dset = np.nan_to_num(np.array(sorted(dataset), 
                                                    dtype=np.float)
                                           )
            sper_freq_lvar_dset = self.spearmanr(freq_lvar_dset[:, 0], 
                                                 freq_lvar_dset[:, 1], 
                                                 True)
            row_res["Rho_Freq_VarStrLen_VAR0"] = sper_freq_lvar_dset[0]
            row_res["P_Freq_VarStrLen_VAR0"] = sper_freq_lvar_dset[1]
            
            # X frequencies Y Mean Lengths varstrl as zero
            dataset = []
            for freq, tokens in bible.tokens_by_frequency.items():
                len_values = []
                for token in tokens:
                    len_values.append(len(token))
                mean_val = statistics.mean(len_values)
                dataset.append((freq, mean_val))
            
            freq_mlen_dset = np.array(sorted(dataset))
            sper_freq_mlen_dset = self.spearmanr(freq_mlen_dset[:, 0], 
                                                freq_mlen_dset[:, 1], 
                                                True)
            
            row_res["Rho_Freq_MeanStrLen_VAR0"] = sper_freq_mlen_dset[0]
            row_res["P_Freq_MeanStrLen_VAR0"] = sper_freq_mlen_dset[1]
            
            # X length_variance Y mean lengths varstrl as zero
            lvar_mlen_dset = np.column_stack((freq_lvar_dset[:, 1],
                                              freq_mlen_dset[:, 1]))
            sper_lvar_mlen_dset = self.spearmanr(lvar_mlen_dset[:, 0],
                                                 lvar_mlen_dset[:, 1],
                                                 True)
            row_res["Rho_VarStrLen_MeanStrLen_VAR0"] = sper_lvar_mlen_dset[0]
            row_res["P_VarStrLen_MeanStrLen_VAR0"] = sper_lvar_mlen_dset[1]
            
            # Steiger's Z
            steiger = psych.r_test(n=len(lvar_mlen_dset), 
                                   r12=row_res["Rho_Freq_VarStrLen_VAR0"], 
                                   r13=row_res["Rho_Freq_MeanStrLen_VAR0"], 
                                   r23=row_res["Rho_VarStrLen_MeanStrLen_VAR0"]
                                   )
            row_res["Steiger_t_Freq_VarStrLen_MeanStrLen_VAR0"] = steiger[2][0]
            row_res["Steiger_p_Freq_VarStrLen_MeanStrLen_VAR0"] = steiger[3][0]
                        
            res.loc[bible.language] = pd.Series(row_res)
        
        return res
        
    def spearman_var_dataframe(self):
        df = self.to_dataframe()
        
        res = pd.DataFrame(columns=["Rho_StrLen_VarFreq", 
                                    "P_StrLen_VarFreq",
                                    "Rho_Freq_VarStrLen", 
                                    "P_Freq_VarStrLen",
                                    ])
        
        for bible in self.bibles:
            row_res = {}
            
            dataset = [(token_length, f_variance) for token_length, f_variance in \
                                        bible.variance_by_tok_length.items()\
                                        if f_variance != None]
            
            len_fvar_dset = np.array(sorted(dataset))
            sper_len_fvar_dset = self.spearmanr(len_fvar_dset[:, 0], 
                                                len_fvar_dset[:, 1], 
                                                True)
            
            row_res["Rho_StrLen_VarFreq"] = sper_len_fvar_dset[0]
            row_res["P_StrLen_VarFreq"] = sper_len_fvar_dset[1]
            
            dataset = [(frequency, l_variance) for frequency, l_variance in \
                                            bible.variance_by_tok_freq.items()
                                            if l_variance != None]
        
            # X frequency Y length_variance 
            freq_lvar_dset = np.array(sorted(dataset))
            sper_freq_lvar_dset = self.spearmanr(freq_lvar_dset[:, 0], 
                                                 freq_lvar_dset[:, 1], 
                                                 True)
            
            row_res["Rho_Freq_VarStrLen"] = sper_freq_lvar_dset[0]
            row_res["P_Freq_VarStrLen"] = sper_freq_lvar_dset[1]
            
            res.loc[bible.language] = pd.Series(row_res)
        
        return res
    
    def spearman_novar_dataframe(self):
        df = self.to_dataframe()
        
        res = pd.DataFrame(columns=["Rho_Freq_StrLen", 
                                    "P_Freq_StrLen",
                                    "Rho_Freq_MeanStrLen", 
                                    "P_Freq_MeanStrLen"
                                    ])
        
        for bible in self.bibles:

            row_res = {}
            dataset = []
            for freq, tokens in bible.tokens_by_frequency.items():
                for token in tokens:
                    dataset.append((freq, len(token)))
        
            # X frequencies Y lengths
            freq_len_dset = np.array(sorted(dataset))
            sper_freq_len_dset = self.spearmanr(freq_len_dset[:, 0], 
                                                freq_len_dset[:, 1], 
                                                True)
            
            row_res["Rho_Freq_StrLen"] = sper_freq_len_dset[0]
            row_res["P_Freq_StrLen"] = sper_freq_len_dset[1]
            
            dataset = []
            for freq, tokens in bible.tokens_by_frequency.items():
                len_values = []
                for token in tokens:
                    len_values.append(len(token))
                mean_val = statistics.mean(len_values)
                dataset.append((freq, mean_val))
            
            # X frequencies Y Mean Lengths
            freq_mlen_dset = np.array(sorted(dataset))
            sper_freq_mlen_dset = self.spearmanr(freq_mlen_dset[:, 0], 
                                                freq_mlen_dset[:, 1], 
                                                True)
            
            row_res["Rho_Freq_MeanStrLen"] = sper_freq_mlen_dset[0]
            row_res["P_Freq_MeanStrLen"] = sper_freq_mlen_dset[1]
            
            res.loc[bible.language] = pd.Series(row_res)
        
        return res

    def spearmanr(self, array1, array2, with_scipy=True):
        x1 = np.ma.masked_invalid(array1)
        y1 = np.ma.masked_invalid(array2)
        m = np.ma.mask_or(np.ma.getmask(x1), np.ma.getmask(y1))
        k = np.ma.array(x1, mask=m, copy=True).compressed()
        j = np.ma.array(y1, mask=m, copy=True).compressed()
        if with_scipy:
            return ss.spearmanr(k, j, nan_policy='omit')
        else:
            return bc.distancematrix((k, j), dist="s")
        
    def to_dataframe(self):
        dataframe = pd.DataFrame(columns=self.column_headers)
        for bible in self.bibles:
            dataframe.loc[bible.language] = pd.Series(bible.as_dict())
        return dataframe