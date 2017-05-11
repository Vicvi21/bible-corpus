# -*- coding:utf-8 -*-

import os
import subprocess

for directory in os.listdir("."):
    if os.path.isdir(directory):
        for dirname in os.listdir("./" + directory):
            if os.path.isdir("./" + directory + "/" +  dirname):
                arg0 ="./{0}/{1}/*.png".format(directory,
                                               dirname)
                if directory == "Random_GEOM_LEN":
                    corpus = "nlfp"
                elif directory == "Random_SAME_FLEN":
                    corpus = "lfp"
                else:
                    corpus = "bibles"
                arg1 = "plots_{0}_{1}.pdf".format(dirname, corpus)
                subprocess.call(["convert", 
                                 arg0, arg1])
