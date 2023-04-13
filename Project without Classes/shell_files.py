# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 16:42:44 2022

@author: Alyssa Blanc
"""

import os

#read k-factors and weights
def read_element_file(fileName):
    """
    Read a shell file and turn it into a list

    Parameters
    ----------
    fileName : str
        Name of file.

    Returns
    -------
    array : list
        List of shell factors.

    """
    array = []
    file = open(fileName)
    for line in file:
        #split the line
        split = line.partition(" ")
        #get the _Ka element name
        eleName = split[0]
        #get the k-factor
        factor = float(split[2])
        #add to list
        array.append((eleName, factor))
    file.close()
    return array

#load txt files and arrays may need to change paths depending on location of k and l files
kFile = os.path.realpath(os.path.dirname(__file__)) + '\\k_factors_K_shell.txt'
k_shells = read_element_file(kFile)
lFile = os.path.realpath(os.path.dirname(__file__)) + '\\k_factors_L_shell.txt'
l_shells = read_element_file(lFile)
