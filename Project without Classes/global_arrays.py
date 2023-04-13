# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 13:20:14 2022

@author: Alyssa Blanc
"""

import tkinter as tk

#element arrays
element_array = [['H','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','He'],
                ['Li','Be','0','0','0','0','0','0','0','0','0','0','B','C','N','O','F','Ne'],
                ['Na','Mg','0','0','0','0','0','0','0','0','0','0','Al','Si','P','S','Cl','Ar'],
                ['K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr'],
                ['Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe'],
                ['Cs','Ba','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'],
                ['Fr','Ra','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo'],
                ['0','0','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','0','0'],
                ['0','0','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','0','0']]
disabled_elements = ['Li','Lr', 'Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No']

#possible element lines array
poss_lines = ['Ka', 'Kb', 'La', 'Lb1', 'Ma', 'Mb']

#color array
color_array = ['Greys',
               'Purples',
               'Blues',
               'Greens',
               'Oranges',
               'Reds']

class Changing_Globals:
    
    def __init__(self):
        """
        Initialize the global variables

        Returns
        -------
        None.

        """
        
        self.data = False
        self.model = False
        self.residual = False
        self.chi_squared = False
        self.maps = False
        self.overlay = False
        
        self.signal = ''
        self.plot = False
        
        self.s = None
        self.m = None
        self.s_model = None
        self.sTEM = None
        
        self.beam = 0
        self.x_axis = []
        
        self.text = None
        self.frame = None
        self.elements = []
        self.shape = None
        
        return
    
    def reset(self):
        """
        Reset the global variables

        Returns
        -------
        None.

        """
        
        self.data = False
        self.model = False
        self.residual = False
        self.chi_squared = False
        self.analysis = False
        self.maps = False
        self.overlay = False
        
        self.signal = ''
        
        self.s = None
        self.m = None
        self.s_model = None
        self.sTEM = None
        
        self.beam = 0
        self.x_axis = []
        
        return
    
class Shape:
    
    def __init__(self):
        """
        Initialize the shape variables

        Returns
        -------
        None.

        """
        
        self.name = ''
        self.made = False
        self.line_made = False
        self.drawing = None
        self.line = None
        
        self.width = None
        
        self.points = []
        self.cords = []
        self.drawn_lines = []
        
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        
        self.x_start = 0
        self.y_start = 0
        self.x_end = 0
        self.y_end = 0
        
        self.line_x_start = 0
        self.line_y_start = 0
        self.line_x_end = 0
        self.line_y_end = 0
        
        self.line_x0 = 0
        self.line_y0 = 0
        self.line_x1 = 0
        self.line_y1 = 0
        
        return