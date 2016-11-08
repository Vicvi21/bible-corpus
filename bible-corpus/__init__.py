# -*- coding:utf-8 -*-


import os
from bible import Bible


source_dir = "../bibles/Usable/"

bibles = []

i = 0
for _, _, filenames in os.walk(source_dir):
    for filename in filenames:
        bibles.append(Bible(source_dir + filename))
        i += 1
        if i == 1:
            break
bible = bibles[0]        
import ipdb;ipdb.set_trace()