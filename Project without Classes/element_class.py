# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 13:24:53 2022

@author: Alyssa Blanc
"""

import tkinter as tk
from global_arrays import disabled_elements
from hyperspy.misc.elements import elements as elements_db
import element_buttons as eb


class Line:
    
    def __init__(self, line, color, ele):
        """
        Initialize the ppssible lines for each element

        Parameters
        ----------
        line : str
            Name of line.
        color : str
            Color of line.
        ele : str
            Element name.

        Returns
        -------
        None.

        """
        
        #name of line
        self.name = line
        self.full_name = ele + '_' + line
        
        #if the line appers in TEM
        self.bool = tk.BooleanVar()
        self.bool.set(False)
        
        #color of the element
        self.color = tk.StringVar()
        self.color.set(color)
        
        #if the line appears on the map
        self.map = tk.BooleanVar()
        self.map.set(False)
        
        return

class Element:
    
    def __init__(self, ele, r, c, color, frame, d, analysis, overlay):
        """
        Initialize all element buttons

        Parameters
        ----------
        ele : str
            Name of element.
        r : int
            Row number of element.
        c : int
            Column number of element.
        color : str
            Color of element.
        frame : tk.Frame
            Periodic table frame.
        d : glb.Changing_Globals
            All global variables.
        analysis : function
            Function for analysis of elements.
        overlay : function
            Function to create element overlays.

        Returns
        -------
        None.

        """
        
        self.name = ele
        self.row = r
        self.column = c
        
        #set lines in element
        self.lines = []
        if self.name not in disabled_elements:
            for line in elements_db[self.name]['Atomic_properties']['Xray_lines']:
                l = Line(line, color, ele)
                self.lines.append(l)
                
        self.shell = tk.IntVar()
        self.shell.set(0)
        
        #make the element button
        self.button = tk.Button(master=frame, text=ele, 
                                font=tk.font.Font(size=7), state= 'disabled')
        self.button.bind("<Button-1>", lambda event: eb.pressed(d, self, analysis, overlay))
        self.button.bind('<Enter>', lambda event: eb.over(d, self))
        self.button.bind('<Leave>', eb.leaving)
        self.button.bind("<Button-3>", lambda event: eb.right_clicked(d, self, analysis, overlay, event))
        self.button.grid(row=r, column=c, sticky='nesw')
        
        return
    
    def reset_variables(self):
        """
        Reset all of the variables for every element

        Returns
        -------
        None.

        """
        
        #reset the button
        self.reset_buttons()
        
        #make the global variables false
        for line in self.lines:
            line.bool.set(False)
            line.map.set(False)
            
        self.shell.set(0)
        
        return
    
    def reset_buttons(self):
        """
        Reset all of the periodic tabel buttons

        Returns
        -------
        None.

        """
        
        #if element should be disabled
        if self.name in disabled_elements:
            self.button.configure(state='disabled', bg='RosyBrown1')
        #else, reset it normally
        else:
            self.button.configure(state='normal', bg='SystemButtonFace')
        
        return
    
    def change_button_color(self):
        """
        Change the color of a button

        Returns
        -------
        None.

        """
        
        #if already enabled
        if self.button.cget('bg') == 'CadetBlue1':
            self.button.configure(bg='SystemButtonFace')
        #if not already enabled
        elif self.button.cget('bg') == 'SystemButtonFace':
            self.button.configure(bg='CadetBlue1')
            
        return
    