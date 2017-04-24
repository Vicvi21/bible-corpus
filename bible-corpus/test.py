# -*- coding:utf-8 -*-


import os
import sys
from bible import Bible
from generate import RandomBible

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

orig = "../bibles/Usable/Chinantec-NT.xml"
rand1 = "../bibles/Random_SAME_FLEN/Chinantec random(keeps long_char frequency).xml"
rand2 = "../bibles/Random_GEOM_LEN/Chinantec random(geometric length).xml"

orig_bible = Bible.from_path(orig)
rand1_bible = Bible.from_path(rand1)
rand2_bible = Bible.from_path(rand2)

def count_chars(bible):
    unique_chars = bible.unique_chars
    original_path = bible.file_path
    xml_tree = ET.ElementTree(file=original_path)
            
    xml_root = xml_tree.getroot()
    xml_header, xml_text = xml_root.getchildren()
    
    char_bag = RandomBible.count_character(unique_chars,
                                           xml_text)
    
    return char_bag

orig_bible_chars = count_chars(orig_bible)
rand1_bible_chars = count_chars(rand1_bible)
rand2_bible_chars = count_chars(rand2_bible)

orig_bible_chars_prob = RandomBible.char_bag_to_probability(orig_bible_chars)
rand1_bible_chars_prob = RandomBible.char_bag_to_probability(rand1_bible_chars)
rand2_bible_chars_prob = RandomBible.char_bag_to_probability(rand2_bible_chars)

print("\tOrig\tRand1\tRand2")
sum_orig_chars = 0
sum_rand1_chars = 0
sum_rand2_chars = 0
for char in orig_bible_chars.keys():
    print("{0}:\t{1}\t{2}\t{3}".format(char,
                                       orig_bible_chars[char],
                                       rand1_bible_chars[char],
                                       rand2_bible_chars[char]))
    
    sum_orig_chars += orig_bible_chars[char]
    sum_rand1_chars += rand1_bible_chars[char]
    sum_rand2_chars += rand2_bible_chars[char]
    
print("%s:\t%.2f\t%.2f\t%.2f" % ("Total",
                                 sum_orig_chars,
                                 sum_rand1_chars,
                                 sum_rand2_chars))
    
print("\nProbabilities\n")
print("\tOrig\tRand1\tRand2")
sum_orig_prob = 0
sum_rand1_prob = 0
sum_rand2_prob = 0
for char in orig_bible_chars_prob.keys():
    print("%s:\t%.2f\t%.2f\t%.2f" % (char,
                                     orig_bible_chars_prob[char],
                                     rand1_bible_chars_prob[char],
                                     rand2_bible_chars_prob[char]))
    sum_orig_prob += orig_bible_chars_prob[char]
    sum_rand1_prob += rand1_bible_chars_prob[char]
    sum_rand2_prob += rand2_bible_chars_prob[char]
    
print("%s:\t%.2f\t%.2f\t%.2f" % ("Total",
                                 sum_orig_prob,
                                 sum_rand1_prob,
                                 sum_rand2_prob))
import ipdb;ipdb.set_trace()